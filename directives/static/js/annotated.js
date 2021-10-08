// Implementation adapted from the programming o1 Course 2020
// https://grader.cs.hut.fi/static/O1_2020/_static/kurssimateriaali.js
jQuery(function ($) {
  const rootElement = $("body");
  var commentPrefix = "comment-";
  var lockedCodeComment = null;

  /* Add interactive highlighters for code examples: */
  rootElement
    .find("div.codecomment.container, span.codecomment")
    .filter("[class^=" + commentPrefix + "],[class*=' " + commentPrefix + "']")
    .each(function () {
      var commentClass = $(this)
        .attr("class")
        .split(" ")
        .filter(function (className) {
          return className.indexOf(commentPrefix) === 0;
        });
      if (commentClass.length != 1) {
        console.error(
          "Unexpected classes on code comment: " + $(this).attr("class")
        );
      }
      var classEnd = commentClass[0].substring(commentPrefix.length);
      var classSepIndex = classEnd.lastIndexOf('-');
      if (classSepIndex === -1) {
        console.error(
          "Unexpected classes on code comment: " + $(this).attr("class")
        );
        classSepIndex = classEnd.length;
      }
      var exampleName = classEnd.substring(0, classSepIndex);
      var commentNumber = classEnd.substring(classSepIndex + 1);
      var commentID = exampleName + "-" + commentNumber;

      /* find all target locations for current commentary box */
      var matchingCodeLocations = $(
        ".ex-" + exampleName + " .loc" + commentNumber
      );
      if (matchingCodeLocations.length === 0) {
        console.error(
          "No code locations match this comment: " + commentClass[0]
        );
      }
      var targets = matchingCodeLocations.find("*").addBack();

      $(this).hover(
        /* add hover effect for each comment and associated code locations: */
        function () {
          // mouse enters

          // To prevent clashes in content, remove lock from any other annotations with a replacement attribute (by programmatically clicking them).
          $(".codecomment.comment-now-locked")
            .not(this)
            .each(function () {
              if (this.hasAttribute("data-replacement")) {
                $(this).click();
                $(this).mouseleave();
              }
            });

          if (this.hasAttribute("data-replacement")) {
            // To prevent clashes in content with this replacement, remove lock from any and all other annotations (by programmatically clicking them).
            $(".codecomment.comment-now-locked")
              .not(this)
              .each(function () {
                $(this).click();
              });

            var replacement = $(this).attr("data-replacement");
            var target = targets.first();
            target.addClass("loc-now-inserted");
            if ($(this).data("original") === undefined) {
              console.log("SAVED");
              $(this).data("original", target.clone());
            }
            target.html(replacement);
          }
          targets.addClass("loc-now-highlighted");
          $(this).addClass("comment-now-highlighted");
        },
        function () {
          // mouse exits
          if (
            this.hasAttribute("data-replacement") &&
            !$(this).hasClass("comment-now-locked")
          ) {
            var originalContent = $(this).data("original");
            targets.first().html(originalContent);
            targets.first().removeClass("loc-now-inserted");
          }
          targets.removeClass("loc-now-highlighted");
          $(this).removeClass("comment-now-highlighted");
        }
      );

      $(this).click(
        /* add click effect for each comment and associated code locations: */
        function () {
          if (lockedCodeComment === commentID) {
            // click again to end lock
            targets.removeClass("loc-now-locked");
            $(this).removeClass("comment-now-locked");
            lockedCodeComment = null;
          } else {
            // click to lock this and unlock everything else
            $(".codecomment.comment-now-locked").each(function () {
              $(this).removeClass("comment-now-locked");
            });
            $(".loc-now-locked").each(function () {
              $(this).removeClass("loc-now-locked");
            });
            targets.addClass("loc-now-locked");
            $(this).addClass("comment-now-locked");
            lockedCodeComment = commentID;
          }
        }
      );
    });

  /* Add interactive highlighters for gui examples: */
  /* to be done: refactor to avoid nasty duplication with the above; also: make more generic so that it can be used with any images later  */
  rootElement
    .find("div.guicomment.container")
    .filter(
      "div[class^=" + commentPrefix + "],div[class*=' " + commentPrefix + "']"
    )
    .each(function () {
      var commentClass = $(this)
        .attr("class")
        .split(" ")
        .filter(function (className) {
          return className.indexOf(commentPrefix) === 0;
        });
      if (commentClass.length != 1) {
        console.error(
          "Unexpected classes on code comment: " + $(this).attr("class")
        );
      }
      var classBits = commentClass[0]
        .substring(commentPrefix.length)
        .split("at");
      if (classBits.length != 2) {
        console.error(
          "Unexpected classes on code comment: " + $(this).attr("class")
        );
      }
      var exampleName = classBits[0];
      var commentNumber = classBits[1];
      var commentID = exampleName + "-" + commentNumber;

      /* find all target locations for current commentary box */
      var targets = rootElement.find(
        ".gui" + exampleName + ".container div.figure img"
      );
      if (targets.length === 0) {
        console.error("No gui examples match this comment: " + commentClass[0]);
      }

      /* add hover effect for each comment and associated code locations: */
      $(this).hover(
        function () {
          var path = targets.eq(0).attr("src").split("/");
          path[path.length - 1] =
            "gui" + exampleName + "_" + commentNumber + ".png";
          targets.attr("src", path.join("/"));
          $(this).addClass("comment-now-highlighted");
        },
        function () {
          var path = targets.eq(0).attr("src").split("/");
          path[path.length - 1] = "gui" + exampleName + ".png";
          targets.attr("src", path.join("/"));
          $(this).removeClass("comment-now-highlighted");
        }
      );
    });
});
