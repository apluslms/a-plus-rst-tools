/* JavaScript for the thebe-button directive.
Source: https://github.com/executablebooks/sphinx-thebe/blob/v0.0.8/sphinx_thebe/_static/sphinx-thebe.js

MIT License

Copyright (c) 2018 Chris Holdgraf

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
/**
 * Add attributes to Thebe blocks to initialize thebe properly
 */

var initThebe = () => {
    // If Thebelab hasn't loaded, wait a bit and try again. This
    // happens because we load ClipboardJS asynchronously.
    if (window.thebelab === undefined) {
        console.log("thebe not loaded, retrying...");
        setTimeout(initThebe, 500)
        return
    }

    console.log("Adding thebe to code cells...");

    // Load thebe config in case we want to update it as some point
    thebe_config = $('script[type="text/x-thebe-config"]')[0]


    // If we already detect a Thebe cell, don't re-run
    if (document.querySelectorAll('div.thebe-cell').length > 0) {
        return;
    }

    // Update thebe buttons with loading message
    $(".thebe-launch-button").each((ii, button) => {
        button.innerHTML = `
        <div class="spinner">
            <div class="rect1"></div>
            <div class="rect2"></div>
            <div class="rect3"></div>
            <div class="rect4"></div>
        </div>
        <span class="loading-text"></span>`;
    })

    // Set thebe event hooks
    var thebeStatus = 'waiting';
    var intervalId;
    thebelab.on("status", function (evt, data) {
        console.log("Status changed:", data.status, data.message);

        // Start a setInterval function to monitor connections, and cancel the previous one
        if (data.status == "ready") intervalId = connectionChecker(intervalId || 0, true)
        if (data.status == "disconnected") intervalId = connectionChecker(intervalId || 0, false)

        // A nicer interface for the state of launch process
        const state_dict = {
            'launching': 'Launching',
            'building': 'Launching',
            'built': 'Launching',
            'starting': 'Launching',
            'pushing': 'Launching',
            'ready': 'Active',
            'failed': 'Error, try refreshing the page or contact course staff',
            'disconnected': 'Disconnected, wait or try refreshing the page'
        }

        // Change status of topmost container
        $(".thebe-info ")
        .removeClass("thebe-status-" + thebeStatus)
        .addClass("thebe-status-" + data.status)

        // Write loading text into standalone button
        $(".thebe-standalone-button-container")
        .find(".thebe-launch-button")
        .find(".loading-text")
        .html(`<span class='launch_msg'>Launching interactive code environment: </span><span class='status'> ${state_dict[data.status]} </span>`);

        // Write status message into button next to code cell
        $(".thebe-status-msg ").html(state_dict[data.status]);

        // Now update our thebe status
        thebeStatus = data.status;

        // Find any cells with an initialization tag and ask thebe to run them when ready
        if (data.status === "ready") {
            var thebeInitCells = document.querySelectorAll('.thebe-init, .tag_thebe-init');
            thebeInitCells.forEach((cell) => {
                console.log("Initializing Thebe with cell: " + cell.id);
                cell.querySelector('.thebelab-run-button').click();
            });
        }
    });


    // Find all code cells, replace with Thebe interactive code cells
    const codeCells = document.querySelectorAll(thebe_selector)
    codeCells.forEach((codeCell, index) => {
        const codeCellId = index => `codecell${index}`;
        codeCell.id = codeCellId(index);
        codeCellText = codeCell.querySelector(thebe_selector_input);
        codeCellOutput = codeCell.querySelector(thebe_selector_output);

        // Clean up the language to make it work w/ CodeMirror and add it to the cell
        dataLanguage = detectLanguage(kernelName);

        if (codeCellText) {
            codeCellText.setAttribute('data-language', dataLanguage);
            codeCellText.setAttribute('data-executable', 'true');

            // If we had an output, insert it just after the `pre` cell
            if (codeCellOutput) {
                $(codeCellOutput).attr("data-output", "");
                $(codeCellOutput).insertAfter(codeCellText);
            }
        }
    });

    // Init thebe
    thebelab.bootstrap();
}

// Helper function to munge the language name
var detectLanguage = (language) => {
    if (language.indexOf('python') > -1) {
        language = "python";
    } else if (language === 'ir') {
        language = "r";
    } else if (language.indexOf('cpp') > -1) {
        language = "text/x-c++src";
    } else if (language.indexOf('c') > -1) {
        language = "text/x-csrc";
    } else if (language.indexOf('octave')) {
        language = "text/x-octave";
    }
    return language;
}


// A function to check whether a kernel is still connected
// A native solution would be better, but I didn't see one
const connectionChecker = (previousInterval, previouslyConnected) => {
    const time_to_failure_ms = 2000 
    const check_interval_ms = 10000

    if (previousInterval) clearInterval(previousInterval)

    const timer = () => (
        new Promise((res) => {
            setTimeout(() => res(false), time_to_failure_ms)
        })
    )

    // Promise that checks whether kernel returns info
    const ack = () => (
        window.thebeKernel
        .requestKernelInfo()
        .then(() => true)
        .catch(() => false)
    )

    const timeOutCheck = () => Promise.race([timer(), ack()])

    intervalId = window.setInterval( (previouslyConnected) => {
        timeOutCheck().then((connected) => {
            if (!connected && previouslyConnected) {
            console.log(`Kernel disconnected`)
            thebelab.events.trigger('status', { 
                status: "disconnected",
                message: "Kernel not responding"
            }) } else if (connected && !previouslyConnected) {
                console.log(`Kernel reconnected`)
                thebelab.events.trigger('status', { 
                    status: "ready",
                    message: "Kernel reconnnected after disconnect"
                })
            }
        })
    },
    check_interval_ms,
    previouslyConnected
    )

    return intervalId
}