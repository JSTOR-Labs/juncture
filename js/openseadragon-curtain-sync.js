'use strict';

(function () {

  // Ensure the console is here; some versions of IE need this.
  window.console = window.console || {};
  window.console.assert = window.console.assert || function () { };
  window.console.error = window.console.error || function () { };

  // ----------
  var CurtainMode = function (args) {
    var self = this;

    this.images = args.images;
    this.startingZoom = args.zoom;
    this.startingPan = args.pan;
    this.isMobile = (typeof window.orientation !== 'undefined') || (navigator.userAgent.indexOf('IEMobile') !== -1);
    // this.isMobile = true; // For testing

    if (this.isMobile) {
      this.clipFactorX = 0.5;
      this.clipFactorY = 0.5;
    } else {
      this.clipFactorX = 0;
      this.clipFactorY = 0;
    }

    OpenSeadragon.EventSource.call(this);

    var ops = args.osdOptions;
    ops.element = args.container;
    this.viewer = OpenSeadragon(ops);

    this.viewer.canvas.style.outline = 'none'; // so we don't see the browser's selection rectangle when we click

    this.tracker = new OpenSeadragon.MouseTracker({
      element: this.viewer.canvas,
      moveHandler: function (event) {
        if (self.isMobile) {
          return;
        }

        self.dragClip(event.position, true, true);
      },
      pressHandler: function (event) {
        if (!self.isMobile) {
          return;
        }

        var shownImages = self.getShownImages();
        if (shownImages.length <= 1) {
          return;
        }

        var viewerPos = new OpenSeadragon.Point(self.viewer.container.clientWidth * self.clipFactorX,
          self.viewer.container.clientHeight * self.clipFactorY);

        var threshold = 20;

        if (shownImages.length === 2) {
          if (Math.abs(viewerPos.x - event.position.x) < threshold) {
            self.isDraggingClipX = true;
          }
        } else if (shownImages.length === 3) {
          if (Math.abs(viewerPos.x - event.position.x) < threshold && event.position.y < viewerPos.y + threshold) {
            self.isDraggingClipX = true;
          }

          if (Math.abs(viewerPos.y - event.position.y) < threshold) {
            self.isDraggingClipY = true;
          }
        }
      },
      releaseHandler: function (event) {
        self.isDraggingClipX = false;
        self.isDraggingClipY = false;
      }
    });

    this.viewer.addHandler('viewport-change', function () {
      self.updateClip();
      self.raiseEvent('change:viewport');
    });

    this.viewer.addHandler('add-item-failed', function (event) {
      self.raiseEvent('add-item-failed', event);
    });

    this.viewer.addHandler('canvas-drag', function (event) {
      if (!self.isDraggingClipX && !self.isDraggingClipY) {
        return;
      }

      event.preventDefaultAction = true;
      self.dragClip(event.position, self.isDraggingClipX, self.isDraggingClipY);
    });

    this.images.forEach(function (image, i) {
      image.curtain = {};

      self.viewer.addTiledImage({
        tileSource: image.tileSource,
        opacity: image.shown,
        success: function (event) {
          image.curtain.tiledImage = event.item;
          image.curtain.tiledImage.setOpacity(image.shown ? 1 : 0);

          if (i === 0) {
            if (self.startingZoom) {
              self.viewer.viewport.zoomTo(self.startingZoom, null, true);
            }

            if (self.startingPan) {
              self.viewer.viewport.panTo(self.startingPan, true);
            }
          }

          self.updateClip();
        }
      });
    });
  };

  // ----------
  CurtainMode.prototype = OpenSeadragon.extend({
    // ----------
    destroy: function () {
      this.images.forEach(function (image) {
        delete image.curtain;
      });

      this.tracker.destroy();
      this.viewer.destroy();
    },

    // ----------
    getZoom: function () {
      return this.viewer.viewport.getZoom();
    },

    // ----------
    setZoom: function (zoom) {
      this.viewer.viewport.zoomTo(zoom, null, true);
      this.startingZoom = zoom;
    },

    // ----------
    getPan: function () {
      return this.viewer.viewport.getCenter();
    },

    // ----------
    setPan: function (pan) {
      this.viewer.viewport.panTo(pan, true);
      this.startingPan = pan;
    },

    // ----------
    zoomIn: function () {
      this.viewer.viewport.zoomBy(this.viewer.zoomPerClick);
      this.viewer.viewport.applyConstraints();
    },

    // ----------
    zoomOut: function () {
      this.viewer.viewport.zoomBy(1 / this.viewer.zoomPerClick);
      this.viewer.viewport.applyConstraints();
    },

    // ----------
    updateImageShown: function (image) {
      if (image.curtain.tiledImage) {
        image.curtain.tiledImage.setOpacity(image.shown ? 1 : 0);
      }
    },

    // ----------
    updateClip: function () {
      var viewerPos = new OpenSeadragon.Point(this.viewer.container.clientWidth * this.clipFactorX,
        this.viewer.container.clientHeight * this.clipFactorY);

      var viewportPos = this.viewer.viewport.pointFromPixel(viewerPos, true);
      var tiledImage, imageSize, imagePos, clip;
      var shownImages = this.getShownImages();

      if (shownImages.length > 1) {
        tiledImage = shownImages[1].curtain.tiledImage;
        if (tiledImage) {
          imageSize = tiledImage.getContentSize();
          imagePos = tiledImage.viewportToImageCoordinates(viewportPos);
          var x = Math.min(imageSize.x, Math.max(0, imagePos.x));
          clip = new OpenSeadragon.Rect(x, 0, imageSize.x, imageSize.y);
          tiledImage.setClip(clip);
        }
      }

      if (shownImages.length > 2) {
        tiledImage = shownImages[2].curtain.tiledImage;
        if (tiledImage) {
          imageSize = tiledImage.getContentSize();
          imagePos = tiledImage.viewportToImageCoordinates(viewportPos);
          var y = Math.min(imageSize.y, Math.max(0, imagePos.y));
          clip = new OpenSeadragon.Rect(0, y, imageSize.x, imageSize.y);
          tiledImage.setClip(clip);
        }
      }
    },

    // ----------
    dragClip: function (position, dragX, dragY) {
      if (dragX) {
        this.clipFactorX = position.x / this.viewer.container.clientWidth;
      }

      if (dragY) {
        this.clipFactorY = position.y / this.viewer.container.clientHeight;
      }

      this.updateClip();
    },

    // ----------
    getShownImages: function () {
      return this.images.filter(function (image) {
        return image.shown;
      });
    }
  }, OpenSeadragon.EventSource.prototype);

  // ----------
  var SyncMode = function (args) {
    var self = this;

    this.images = args.images;
    this.startingZoom = args.zoom;
    this.startingPan = args.pan;
    this.leadingImage = null;

    OpenSeadragon.EventSource.call(this);

    this.innerContainer = document.createElement('div');
    this.innerContainer.style.display = 'flex';
    this.innerContainer.style.height = '100%';
    args.container.appendChild(this.innerContainer);

    this.images.forEach(function (image, i) {
      image.sync = {};

      image.sync.container = document.createElement('div');
      image.sync.container.style.flexGrow = 1;
      self.innerContainer.appendChild(image.sync.container);

      if (!image.shown) {
        image.sync.container.style.display = 'none';
      }

      var ops = args.osdOptions;
      ops.element = image.sync.container;
      ops.tileSources = image.tileSource;
      image.sync.viewer = OpenSeadragon( ops );

      image.sync.viewer.canvas.style.outline = 'none'; // so we don't see the browser's selection rectangle when we click

      image.sync.viewer.addHandler('open', function () {
        if (self.startingZoom) {
          image.sync.viewer.viewport.zoomTo(self.startingZoom, null, true);
        }

        if (self.startingPan) {
          image.sync.viewer.viewport.panTo(self.startingPan, true);
        } else {
          var bounds = image.sync.viewer.world.getHomeBounds();
          var pan = new OpenSeadragon.Point(bounds.x + (bounds.width / 2), bounds.y + (bounds.height / 2));
          image.sync.viewer.viewport.panTo(pan, true);
        }
      });

      image.sync.viewer.addHandler('add-item-failed', function (event) {
        self.raiseEvent('add-item-failed', event);
      });

      var changeHandler = function () {
        if (self.leadingImage && self.leadingImage !== image) {
          return;
        }

        self.leadingImage = image;
        self.images.forEach(function (image2) {
          if (image2 === image) {
            return;
          }

          image2.sync.viewer.viewport.zoomTo(image.sync.viewer.viewport.getZoom());
          image2.sync.viewer.viewport.panTo(image.sync.viewer.viewport.getCenter());
        });

        self.leadingImage = null;
      };

      image.sync.viewer.addHandler('zoom', function () {
        changeHandler();
      });

      image.sync.viewer.addHandler('pan', function () {
        changeHandler();
      });

      if (i === 0) {
        image.sync.viewer.addHandler('viewport-change', function () {
          self.raiseEvent('change:viewport');
        });
      }
    });
  };

  // ----------
  SyncMode.prototype = OpenSeadragon.extend({
    // ----------
    destroy: function () {
      this.images.forEach(function (image) {
        image.sync.container.parentNode.removeChild(image.sync.container);
        image.sync.viewer.destroy();
        delete image.sync;
      });

      this.innerContainer.parentNode.removeChild(this.innerContainer);
    },

    // ----------
    getZoom: function () {
      var viewer = this.images[0].sync.viewer;
      return viewer.viewport.getZoom();
    },

    // ----------
    setZoom: function (zoom) {
      var viewer = this.images[0].sync.viewer;
      viewer.viewport.zoomTo(zoom, null, true);
      this.startingZoom = zoom;
    },

    // ----------
    getPan: function () {
      var viewer = this.images[0].sync.viewer;
      return viewer.viewport.getCenter();
    },

    // ----------
    setPan: function (pan) {
      var viewer = this.images[0].sync.viewer;
      viewer.viewport.panTo(pan, true);
      this.startingPan = pan;
    },

    // ----------
    zoomIn: function () {
      var viewer = this.images[0].sync.viewer;
      viewer.viewport.zoomBy(viewer.zoomPerClick);
      viewer.viewport.applyConstraints();
    },

    // ----------
    zoomOut: function () {
      var viewer = this.images[0].sync.viewer;
      viewer.viewport.zoomBy(1 / viewer.zoomPerClick);
      viewer.viewport.applyConstraints();
    },

    // ----------
    updateImageShown: function (image) {
      image.sync.container.style.display = image.shown ? 'block' : 'none';
    }
  }, OpenSeadragon.EventSource.prototype);

  // ----------
  window.CurtainSyncViewer = function (args) {
    var self = this;

    console.assert(args, '[CurtainSyncViewer] args is required');
    console.assert(args.container, '[CurtainSyncViewer] args.container is required');
    console.assert(args.images, '[CurtainSyncViewer] args.images is required');
    console.assert(args.images.length > 0, '[CurtainSyncViewer] args.images must have at least 1 image');

    OpenSeadragon.EventSource.call(this);

    this.container = args.container;
    this.viewportEventThrottle = args.viewportEventThrottle || 250;
    this.lastViewportEventTime = 0;
    this.images = [];
    this.osdOptions = args.osdOptions || {};
    this.osdOptions.showNavigationControl = false; // hardcode to override this option

    if (getComputedStyle(this.container).position === 'static') {
      this.container.style.position = 'relative';
    }

    args.images.forEach(function (argsImage, i) {
      console.assert(argsImage.key, '[CurtainSyncViewer] args.images[' + i + '].key is required');
      console.assert(argsImage.tileSource, '[CurtainSyncViewer] args.images[' + i + '].tileSource is required');

      var image = {
        key: argsImage.key,
        tileSource: argsImage.tileSource,
        shown: !!argsImage.shown
      };

      self.images.push(image);
    });

    this.setMode(args.mode || 'curtain');
  };

  // ----------
  window.CurtainSyncViewer.prototype = OpenSeadragon.extend({
    // ----------
    getMode: function () {
      return this.modeKey;
    },

    // ----------
    setMode: function (key) {
      var self = this;

      console.assert(key === 'curtain' || key === 'sync', '[CurtainSyncViewer.setMode] Must have valid key.');
      if (key === this.modeKey) {
        return;
      }

      if (this.mode) {
        this.mode.destroy();
      }

      this.modeKey = key;

      var config = {
        container: this.container,
        images: this.images,
        zoom: this.zoom,
        pan: this.pan,
        osdOptions: OpenSeadragon.extend({}, this.osdOptions)
      };

      if (key === 'curtain') {
        this.mode = new CurtainMode(config);
      } else { // sync
        this.mode = new SyncMode(config);
      }

      this.mode.addHandler('change:viewport', function () {
        self.handleViewportChange();
      });

      this.mode.addHandler('add-item-failed', function (event) {
        self.raiseEvent('open-failed', {
          message: event.message || '',
          tileSource: event.options ? event.options.tileSource : undefined
        });
      });

      this.raiseEvent('change:mode');
    },

    // ----------
    getZoom: function () {
      return this.mode.getZoom();
    },

    // ----------
    setZoom: function (zoom) {
      console.assert(typeof zoom === 'number' && zoom > 0 && zoom < Infinity, '[CurtainSyncViewer.setZoom] zoom must be a positive number');
      this.mode.setZoom(zoom);
      this.handleViewportChange();
    },

    // ----------
    zoomIn: function () {
      this.mode.zoomIn();
      this.handleViewportChange();
    },

    // ----------
    zoomOut: function () {
      this.mode.zoomOut();
      this.handleViewportChange();
    },

    // ----------
    getPan: function () {
      return this.mode.getPan();
    },

    // ----------
    setPan: function (pan) {
      console.assert(typeof pan === 'object' && typeof pan.x === 'number' && typeof pan.y === 'number',
        '[CurtainSyncViewer.setPan] pan must be an object with an x and a y');

      this.mode.setPan(new OpenSeadragon.Point(pan.x, pan.y));
      this.handleViewportChange();
    },

    // ----------
    getImageShown: function (key) {
      var shown = false;
      this.images.forEach(function (image) {
        if (image.key === key && image.shown) {
          shown = true;
        }
      });

      return shown;
    },

    // ----------
    setImageShown: function (key, shown) {
      var self = this;
      shown = !!shown;
      var changed = false;
      this.images.forEach(function (image) {
        if (image.key === key && image.shown !== shown) {
          changed = true;
          image.shown = shown;
          self.mode.updateImageShown(image);
        }
      });

      if (changed) {
        this.raiseEvent('change:imageShown', {
          key: key
        });
      }
    },

    // ----------
    handleViewportChange: function () {
      var self = this;
      var zoom = this.getZoom();
      var pan = this.getPan();

      if (this.zoom !== zoom || !this.pan || this.pan.x !== pan.x || this.pan.y !== pan.y) {
        if (!this.viewportEventTimeout) {
          var now = Date.now();
          var diff = now - this.lastViewportEventTime;
          if (diff < this.viewportEventThrottle) {
            this.viewportEventTimeout = setTimeout(function () {
              self.viewportEventTimeout = null;
              self.raiseEvent('change:viewport');
              self.lastViewportEventTime = Date.now();
            }, this.viewportEventThrottle - diff);
          } else {
            this.raiseEvent('change:viewport');
            this.lastViewportEventTime = now;
          }
        }
      }

      this.zoom = zoom;
      this.pan = pan;
    }
  }, OpenSeadragon.EventSource.prototype);

})();
