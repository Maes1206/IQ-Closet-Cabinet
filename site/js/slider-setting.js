/*---------------------------------------------------------------------
    File Name: slider-setting.js
---------------------------------------------------------------------*/
"use strict";

var tpj = jQuery;
var revapi486;

tpj(document).ready(function () {
  if (tpj("#rev_slider_486_1").revolution == undefined) {
    revslider_showDoubleJqueryError("#rev_slider_486_1");
  } else {
    revapi486 = tpj("#rev_slider_486_1").show().revolution({
      sliderType: "standard",
      jsFileLocation: "revolution/js/",
      sliderLayout: "fullscreen",
      dottedOverlay: "none",
      delay: 5000,
      navigation: {
        keyboardNavigation: "on",
        keyboard_direction: "horizontal",
        mouseScrollNavigation: "off",
        mouseScrollReverse: "default",
        onHoverStop: "on",
        touch: {
          touchenabled: "on",
          swipe_threshold: 75,
          swipe_min_touches: 1,
          swipe_direction: "horizontal",
          drag_block_vertical: false
        },
        arrows: {
          style: "gyges",
          enable: true,
          hide_onmobile: false,
          hide_onleave: true,
          hide_delay: 200,
          hide_delay_mobile: 1200,
          tmp: "",
          left: { h_align: "left", v_align: "center", h_offset: 0, v_offset: 0 },
          right:{ h_align: "right", v_align: "center", h_offset: 0, v_offset: 0 }
        },
        bullets: {
          enable: true,
          hide_onmobile: true,
          hide_under: 800,
          style: "hebe",
          hide_onleave: false,
          direction: "horizontal",
          h_align: "center",
          v_align: "bottom",
          h_offset: 0,
          v_offset: 30,
          space: 5,
          tmp: '<span class="tp-bullet-image"></span><span class="tp-bullet-imageoverlay"></span><span class="tp-bullet-title"></span>'
        }
      },
      viewPort: { enable: true, outof: "pause", visible_area: "70%", presize: false },
      responsiveLevels: [1240, 1024, 778, 480],
      visibilityLevels: [1240, 1024, 778, 480],
      gridwidth: [1240, 1024, 778, 480],
      gridheight: [500, 450, 400, 350],
      lazyType: "none",
      parallax: {
        type: "scroll",
        origo: "enterpoint",
        speed: 400,
        levels: [5,10,15,20,25,30,35,40,45,50,46,47,48,49,50,55]
      },
      shadow: 0,
      spinner: "off",
      stopLoop: "off",
      stopAfterLoops: -1,
      stopAtSlide: -1,
      shuffle: "off",
      autoHeight: "off",
      hideThumbsOnMobile: "off",
      hideSliderAtLimit: 0,
      hideCaptionAtLimit: 0,
      hideAllCaptionAtLilmit: 0,
      debugMode: false,
      fallbacks: {
        simplifyAll: "off",
        nextSlideOnWindowFocus: "off",
        disableFocusListener: false
      }
    });

    /* ========= Cambiar imágenes de fondo por JS, sincronizado con el slide ========= */
    // 1) Array de imágenes (una por slide, en orden)
    var images = [
      "img/banner1.png",
      "img/banner2.jpg",
      "img/banner3.pmg"
    ];

    // 2) Al inicializar, asigna la imagen a cada <li> (por si el HTML no trae <img class="rev-slidebg"> con src correcto)
    tpj("#rev_slider_486_1").find("li.rs-slide").each(function(i){
      var $bg = tpj(this).find(".rev-slidebg");
      if ($bg.length) {
        var src = images[i % images.length];
        $bg.attr("src", src).attr("data-lazyload", src);
      }
    });

    // 3) Cuando cambia el slide, asegura que el fondo coincida con el índice del slide (texto e imagen cambian juntos)
    revapi486.on("revolution.slide.onchange", function(e, data){
      // data.slideIndex es 1-based
      var idx = (data.slideIndex - 1) % images.length;
      var $current = tpj(data.currentslide); // <li> activo
      var $bg = $current.find(".rev-slidebg");
      if ($bg.length) {
        var src = images[idx];
        // Cambiamos la imagen (usa lazyload si está activo)
        $bg.attr("src", src).attr("data-lazyload", src);
      }
    });

    // (Opcional) Forzar precarga para evitar parpadeo en el primer cambio
    images.forEach(function(src){
      var img = new Image();
      img.src = src;
    });
  }
});
