/**
 * MIMOSA — homepage intro.
 *
 *  - Live flame drawn by a small WebGL fragment shader (noise-driven body,
 *    blue root, warm glow, heat haze shimmering above). The flame leans when
 *    the cursor moves past it, like a real candle in a draught.
 *  - The photos live in CSS 3D space; the pointer (or a slow drift / device
 *    tilt on phones) turns the scene for a deep parallax.
 *  - Scrolling flies the camera through the photos; the last one fills the
 *    screen and dissolves into the next section.
 *
 * No libraries. Animates transform/opacity and the canvas only.
 * Reduced motion: the CSS shows one still, lit scene and this script exits.
 */
(function () {
    'use strict';

    var root = document.querySelector('[data-intro]');
    if (!root) return;

    var html = document.documentElement;
    if (!html.classList.contains('motion')) return;

    var stage = root.querySelector('.intro__stage');
    var scene = root.querySelector('[data-intro-scene]');
    var content = root.querySelector('[data-intro-content]');
    var light = root.querySelector('.intro__light');
    var fade = root.querySelector('.intro__fade');
    var cue = root.querySelector('.intro__cue');
    var canvas = root.querySelector('[data-intro-flame]');
    var photos = Array.prototype.slice.call(root.querySelectorAll('.intro__ph'));
    var dest = root.querySelector('.intro__ph--dest');

    var PERSPECTIVE = 1000;
    var touch = window.matchMedia('(hover: none), (pointer: coarse)').matches;
    var seen = html.classList.contains('intro-seen');
    try { sessionStorage.setItem('mimosa-intro', '1'); } catch (e) { /* private mode */ }

    function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
    function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
    function smooth(a, b, v) { var t = clamp((v - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); }

    /* ------------------------------------------------------------------
       WebGL flame
       ------------------------------------------------------------------ */
    var VERT = 'attribute vec2 p;varying vec2 v;void main(){v=p*.5+.5;gl_Position=vec4(p,0.,1.);}';
    var FRAG = [
        'precision mediump float;',
        'uniform vec2 uRes;uniform float uTime;uniform float uIgnite;uniform float uWind;',
        'varying vec2 v;',
        'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
        'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);',
        ' return mix(mix(h(i),h(i+vec2(1.,0.)),f.x),mix(h(i+vec2(0.,1.)),h(i+vec2(1.,1.)),f.x),f.y);}',
        'float fbm(vec2 p){float s=0.,a=.5;for(int i=0;i<4;i++){s+=a*n(p);p*=2.03;a*=.5;}return s;}',
        'void main(){',
        ' float asp=uRes.x/uRes.y;',
        ' vec2 p=vec2((v.x-.5)*asp,v.y-.2);',
        ' float t=uTime;',
        ' float H=.2*uIgnite*(1.+.07*(n(vec2(t*2.7,0.))-.5));',
        // heat haze: wobble the space above the flame
        ' float haze=smoothstep(.02,.16,p.y)*(1.-smoothstep(.45,.8,p.y));',
        ' vec2 q=p+vec2((fbm(vec2(p.x*9.,p.y*6.-t*2.3))-.5)*.03*haze,0.);',
        ' float y=q.y/max(H,.001);',
        ' float sway=(fbm(vec2(t*.6,y*1.3-t*1.2))-.5)*.05*y*y+uWind*.05*y*y;',
        ' float x=q.x-sway;',
        ' float w=.042*sqrt(max(0.,1.-y))*smoothstep(-.28,.18,y);',
        ' float nz=fbm(vec2(x*26.,y*4.-t*4.2));',
        ' float d=abs(x)/max(w,1e-4);',
        ' float body=(1.-smoothstep(.5,1.05,d+(nz-.5)*.55*y))*(1.-smoothstep(.72,1.06,y+(nz-.5)*.28))*smoothstep(-.3,-.06,y);',
        ' vec3 edge=vec3(.96,.4,.12);vec3 mid=vec3(1.,.75,.33);vec3 core=vec3(1.,.97,.88);',
        ' float inner=(1.-smoothstep(0.,.62,d))*(1.-smoothstep(.2,.95,y));',
        ' vec3 col=mix(edge,mid,smoothstep(.05,.75,body));col=mix(col,core,inner*body);',
        ' float blue=(1.-smoothstep(-.02,.16,y))*smoothstep(-.3,-.06,y)*(1.-smoothstep(.3,.95,d));',
        ' col=mix(col,vec3(.36,.46,1.),blue*.55);',
        ' float r=length(vec2(q.x*1.1,q.y-H*.42));',
        ' float flick=.93+.07*sin(t*7.3)*sin(t*3.1+1.3);',
        ' float glow=(exp(-r*8.5)*.5+exp(-r*26.)*.55)*uIgnite*flick;',
        ' float sh=haze*(1.-smoothstep(0.,.16,abs(p.x)))*max(fbm(vec2(p.x*16.,p.y*5.-t*3.2))-.48,0.)*.22;',
        ' vec3 c=col*body+vec3(1.,.62,.28)*glow+vec3(1.,.8,.55)*sh;',
        ' gl_FragColor=vec4(c,clamp(max(body,glow+sh),0.,1.));',
        '}'
    ].join('\n');

    var gl = null;
    var uRes, uTime, uIgnite, uWind;

    function initGL() {
        if (!canvas) return false;
        var lowEnd =
            (navigator.connection && navigator.connection.saveData) ||
            (navigator.deviceMemory && navigator.deviceMemory < 4) ||
            (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4);
        if (lowEnd) return false;
        try {
            gl = canvas.getContext('webgl', { alpha: true, antialias: false, premultipliedAlpha: true, powerPreference: 'low-power' });
        } catch (e) { gl = null; }
        if (!gl) return false;

        function shader(type, src) {
            var s = gl.createShader(type);
            gl.shaderSource(s, src);
            gl.compileShader(s);
            return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null;
        }
        var vs = shader(gl.VERTEX_SHADER, VERT);
        var fs = shader(gl.FRAGMENT_SHADER, FRAG);
        if (!vs || !fs) { gl = null; return false; }
        var prog = gl.createProgram();
        gl.attachShader(prog, vs);
        gl.attachShader(prog, fs);
        gl.linkProgram(prog);
        if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { gl = null; return false; }
        gl.useProgram(prog);

        var buf = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buf);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
        var loc = gl.getAttribLocation(prog, 'p');
        gl.enableVertexAttribArray(loc);
        gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

        uRes = gl.getUniformLocation(prog, 'uRes');
        uTime = gl.getUniformLocation(prog, 'uTime');
        uIgnite = gl.getUniformLocation(prog, 'uIgnite');
        uWind = gl.getUniformLocation(prog, 'uWind');
        gl.clearColor(0, 0, 0, 0);
        resizeGL();
        return true;
    }

    function resizeGL() {
        if (!gl) return;
        var dpr = Math.min(window.devicePixelRatio || 1, 1.5);
        var w = Math.max(1, Math.round(canvas.clientWidth * dpr));
        var h = Math.max(1, Math.round(canvas.clientHeight * dpr));
        if (canvas.width !== w || canvas.height !== h) {
            canvas.width = w;
            canvas.height = h;
            gl.viewport(0, 0, w, h);
        }
        gl.uniform2f(uRes, w, h);
    }

    if (initGL()) {
        root.classList.add('is-gl');
    } else {
        root.classList.add('is-lite');
    }

    /* ------------------------------------------------------------------
       State
       ------------------------------------------------------------------ */
    var start = performance.now();
    var progress = 0;
    var pointer = { x: 0, y: 0, active: false };
    var tilt = { x: 0, y: 0, active: false };
    var look = { x: 0, y: 0 };
    var wind = 0;
    var lastPointerX = null;
    var visible = true;
    var running = false;
    var flight = 0;          // camera travel in px needed to fill the screen
    var destX = 0;
    var destY = 0;
    var slowFrames = 0;
    var frames = 0;
    var lastFrame = 0;

    function measure() {
        var vw = window.innerWidth;
        var vh = window.innerHeight;
        if (dest) {
            var w0 = dest.offsetWidth;
            var h0 = dest.offsetHeight;
            var cs = getComputedStyle(dest);
            var mobile = window.matchMedia('(max-width: 767px)').matches;
            destX = parseFloat(cs.getPropertyValue(mobile ? '--mx' : '--x')) * vw / 100 || 0;
            destY = parseFloat(cs.getPropertyValue(mobile ? '--my' : '--y')) * vh / 100 || 0;
            // Vanishing point sits at 46% of the stage height.
            destY += vh * 0.04;
            var s = Math.max(vw / w0, vh / h0) * 1.08;
            var zDest = parseFloat(dest.getAttribute('data-z')) || -2600;
            flight = PERSPECTIVE * (1 - 1 / s) - zDest;
        }
        resizeGL();
    }

    function readScroll() {
        var rect = root.getBoundingClientRect();
        var travel = rect.height - window.innerHeight;
        progress = travel > 0 ? clamp(-rect.top / travel, 0, 1) : 0;
    }

    /* ------------------------------------------------------------------
       Input
       ------------------------------------------------------------------ */
    if (!touch) {
        root.addEventListener('pointermove', function (e) {
            pointer.x = (e.clientX / window.innerWidth) * 2 - 1;
            pointer.y = (e.clientY / window.innerHeight) * 2 - 1;
            pointer.active = true;
            if (lastPointerX !== null) {
                wind = clamp(wind + (e.clientX - lastPointerX) * 0.012, -1.4, 1.4);
            }
            lastPointerX = e.clientX;
            wake();
        }, { passive: true });
        root.addEventListener('pointerenter', function () {
            document.body.classList.add('cursor-in-intro');
        });
        root.addEventListener('pointerleave', function () {
            document.body.classList.remove('cursor-in-intro');
            pointer.active = false;
            lastPointerX = null;
        });
    } else if (window.DeviceOrientationEvent && typeof DeviceOrientationEvent.requestPermission !== 'function') {
        // Android & co: tilt without asking for any permission.
        window.addEventListener('deviceorientation', function (e) {
            if (e.gamma === null || e.beta === null) return;
            tilt.x = clamp(e.gamma / 25, -1, 1);
            tilt.y = clamp((e.beta - 45) / 25, -1, 1);
            tilt.active = true;
        }, { passive: true });
    }

    /* ------------------------------------------------------------------
       Frame
       ------------------------------------------------------------------ */
    function frame(now) {
        if (!visible || document.hidden) { running = false; return; }
        var t = (now - start) / 1000;

        // Watch the frame rate; drop to the CSS flame on a struggling device.
        if (gl && lastFrame) {
            frames += 1;
            if (now - lastFrame > 45) slowFrames += 1;
            if (frames === 90 && slowFrames > 45 && location.search.indexOf('introgl') < 0) {
                gl = null;
                root.classList.remove('is-gl');
                root.classList.add('is-lite');
            }
        }
        lastFrame = now;

        var tx = 0;
        var ty = 0;
        if (pointer.active) {
            tx = pointer.x;
            ty = pointer.y;
        } else if (tilt.active) {
            tx = tilt.x;
            ty = tilt.y;
        } else {
            tx = Math.sin(t * 0.33) * 0.45;
            ty = Math.cos(t * 0.26) * 0.3;
        }
        look.x += (tx - look.x) * 0.05;
        look.y += (ty - look.y) * 0.05;
        wind *= 0.94;

        var p = ease(progress);
        var calm = 1 - smooth(0, 0.35, progress);
        var cam = p * flight;
        var rx = -look.y * 5 * calm;
        var ry = look.x * 7 * calm;
        scene.style.transform =
            'translate3d(' + (-destX * p).toFixed(1) + 'px,' + (-destY * p).toFixed(1) + 'px,' + cam.toFixed(1) + 'px)' +
            ' rotateX(' + rx.toFixed(2) + 'deg) rotateY(' + ry.toFixed(2) + 'deg)';

        for (var i = 0; i < photos.length; i++) {
            var ph = photos[i];
            if (ph === dest) continue;
            var zEff = (ph._z || 0) + cam;
            var op = clamp((PERSPECTIVE * 0.9 - zEff) / (PERSPECTIVE * 0.35), 0, 1);
            if (ph._op !== op) {
                ph.style.opacity = op.toFixed(3);
                ph._op = op;
            }
        }
        if (dest) dest.style.setProperty('--dest-dim', (0.55 * (1 - smooth(0.1, 0.8, progress))).toFixed(3));

        var out = smooth(0, 0.24, progress);
        content.style.opacity = (1 - out).toFixed(3);
        content.style.transform = 'translate3d(0,' + (-out * 90).toFixed(1) + 'px,0) scale(' + (1 + out * 0.06).toFixed(3) + ')';
        content.style.visibility = out >= 1 ? 'hidden' : '';
        var lightOut = smooth(0, 0.4, progress);
        light.style.opacity = (1 - lightOut).toFixed(3);
        light.style.transform = 'translate3d(0,' + (lightOut * 60).toFixed(1) + 'px,0) scale(' + (1 + lightOut * 1.6).toFixed(3) + ')';
        fade.style.opacity = smooth(0.7, 1, progress).toFixed(3);
        if (cue) cue.style.opacity = (1 - smooth(0, 0.05, progress)).toFixed(3);

        if (gl && lightOut < 1) {
            var ignite = seen ? 1 : smooth(0.15, 1.05, t);
            gl.uniform1f(uTime, t);
            gl.uniform1f(uIgnite, ignite);
            gl.uniform1f(uWind, wind);
            gl.clear(gl.COLOR_BUFFER_BIT);
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        }

        window.requestAnimationFrame(frame);
    }

    function wake() {
        if (!running && visible && !document.hidden) {
            running = true;
            window.requestAnimationFrame(frame);
        }
    }

    photos.forEach(function (ph) { ph._z = parseFloat(ph.getAttribute('data-z')) || 0; });

    if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
            visible = entries[0].isIntersecting;
            wake();
        }).observe(root);
    }

    document.addEventListener('visibilitychange', wake);
    window.addEventListener('scroll', function () { readScroll(); wake(); }, { passive: true });
    window.addEventListener('resize', function () { measure(); readScroll(); wake(); }, { passive: true });
    window.addEventListener('load', function () { measure(); wake(); });

    measure();
    readScroll();
    wake();
})();
