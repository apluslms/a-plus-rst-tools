jQuery(function ($) {
  $("div.rst-tabs").each(function () {
    let tabNav = $("<ul />", { class: "tab-nav-aplus" });
    let i = 0;

    $(".tab-content", this).each(function () {
      var sel_item = $("<li />", {
        class: $(this).attr("id"),
        text: $(this).find(".tab-title").text(),
      });
      $(this).find(".tab-title").remove();
      if (i++) {
        $(this).hide();
      } else {
        sel_item.addClass("selected");
      }
      tabNav.append(sel_item);
      $(this).addClass("tab-content-aplus");
    });

    $(".tab-content", this).eq(0).before(tabNav);
    tabNav = null;
    i = null;
  });

  $(".tab-nav-aplus li").click(function (evt) {
    evt.preventDefault();

    var tabsblock = $(this).parents(".rst-tabs");

    var sel_class = $(this).attr("class");
    $("div.tab-content-aplus", tabsblock).hide();
    $("div#" + sel_class, tabsblock).show();

    $("ul.tab-nav-aplus li", tabsblock).removeClass("selected");
    $("ul.tab-nav-aplus li." + sel_class, tabsblock).addClass("selected");

    sel_class = null;
  });
});
