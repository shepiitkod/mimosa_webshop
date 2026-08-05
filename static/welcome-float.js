(function () {
    'use strict';

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    function clamp(v, min, max) {
        return Math.max(min, Math.min(max, v));
    }

    function rand(min, max) {
        return min + Math.random() * (max - min);
    }

    function lerp(a, b, t) {
        return a + (b - a) * t;
    }

    function initWelcomeFloat() {
        var root = document.querySelector('.welcome-float');
        if (!root) return;

        var stage = root.querySelector('.welcome-float__stage');
        var content = root.querySelector('.welcome-float__content');
        var pieces = Array.prototype.slice.call(
            root.querySelectorAll('.welcome-float__piece')
        );

        if (!stage || !pieces.length) return;

        if (reduceMotion.matches) {
            root.classList.add('welcome-float--static', 'is-inview');
            return;
        }

        var depthConfig = {
            far: {
                size: [70, 92],
                wind: [-46, -34],
                opacity: [0.28, 0.42],
                blur: 1.6,
                massScale: 0.72,
                z: 1,
            },
            mid: {
                size: [96, 124],
                wind: [-68, -50],
                opacity: [0.55, 0.72],
                blur: 0.35,
                massScale: 1,
                z: 2,
            },
            near: {
                size: [118, 148],
                wind: [-88, -64],
                opacity: [0.78, 0.94],
                blur: 0,
                massScale: 1.35,
                z: 3,
            },
        };

        var bodies = [];
        var width = 0;
        var height = 0;
        var rafId = 0;
        var lastTs = 0;
        var running = false;
        var pointer = { x: 0, y: 0, tx: 0, ty: 0 };
        var hasPointer = false;

        function measure() {
            var rect = stage.getBoundingClientRect();
            width = Math.max(rect.width, 1);
            height = Math.max(rect.height, 1);
        }

        function spawnBody(el, index, fromRight) {
            var depth = el.getAttribute('data-depth') || 'mid';
            var cfg = depthConfig[depth] || depthConfig.mid;
            var size = rand(cfg.size[0], cfg.size[1]);
            var mass = (size * size * 0.0001 + rand(0.7, 1.15)) * cfg.massScale;
            var lanes = Math.max(pieces.length, 1);
            var preferredY =
                height * (0.1 + (index / Math.max(lanes - 1, 1)) * 0.62) +
                rand(-12, 12);
            var x = fromRight
                ? width + rand(40, 160) + index * 170
                : ((index + 0.5) / lanes) * width + rand(-40, 40);
            var y = preferredY;
            var wind = rand(cfg.wind[0], cfg.wind[1]);

            el.style.width = size + 'px';
            el.style.zIndex = String(cfg.z);
            el.style.setProperty('--piece-blur', cfg.blur + 'px');

            return {
                el: el,
                depth: depth,
                cfg: cfg,
                x: x,
                y: y,
                vx: wind / mass,
                vy: rand(-5, 5) / mass,
                rot: rand(-8, 8),
                vr: rand(-10, 10) / mass,
                mass: mass,
                size: size,
                preferredY: preferredY,
                phase: rand(0, Math.PI * 2),
                baseOpacity: rand(cfg.opacity[0], cfg.opacity[1]),
                wind: wind,
                enter: fromRight ? 0 : 1,
            };
        }

        function resetBodies(fromRight) {
            bodies = pieces.map(function (el, index) {
                return spawnBody(el, index, !!fromRight);
            });
        }

        function softCollide(a, b) {
            if (a.depth !== b.depth) return;

            var dx = b.x - a.x;
            var dy = b.y - a.y;
            var minDist = (a.size + b.size) * 0.58;
            var distSq = dx * dx + dy * dy;
            if (distSq <= 0.0001 || distSq >= minDist * minDist) return;

            var dist = Math.sqrt(distSq);
            var nx = dx / dist;
            var ny = dy / dist;
            var overlap = minDist - dist;
            var invMass = 1 / a.mass + 1 / b.mass;
            var correction = (overlap / invMass) * 0.48;

            a.x -= nx * correction * (1 / a.mass);
            a.y -= ny * correction * (1 / a.mass);
            b.x += nx * correction * (1 / b.mass);
            b.y += ny * correction * (1 / b.mass);

            var rvx = b.vx - a.vx;
            var rvy = b.vy - a.vy;
            var velN = rvx * nx + rvy * ny;
            if (velN > 0) return;

            var impulse = (-(1 + 0.28) * velN) / invMass;
            a.vx -= (impulse * nx) / a.mass;
            a.vy -= (impulse * ny) / a.mass;
            b.vx += (impulse * nx) / b.mass;
            b.vy += (impulse * ny) / b.mass;
            a.vr -= impulse * 0.02;
            b.vr += impulse * 0.02;
        }

        function step(dt) {
            var i;
            var j;
            var body;

            pointer.x = lerp(pointer.x, pointer.tx, 0.06);
            pointer.y = lerp(pointer.y, pointer.ty, 0.06);

            var px = pointer.x * 18;
            var py = pointer.y * 10;

            if (content) {
                content.style.transform =
                    'translate3d(' +
                    (pointer.x * -8).toFixed(2) +
                    'px,' +
                    (pointer.y * -5).toFixed(2) +
                    'px,0)';
            }

            for (i = 0; i < bodies.length; i += 1) {
                body = bodies[i];
                body.enter = Math.min(1, body.enter + dt * 1.4);

                var bob =
                    Math.sin(lastTs * 0.0011 + body.phase) * (14 / body.mass);
                var spring = (body.preferredY - body.y) * (0.42 / body.mass);
                var drag = Math.pow(0.99, dt * 60);

                body.vx += (body.wind / body.mass) * dt;
                body.vy += (bob + spring) * dt;
                body.vx *= drag;
                body.vy *= drag;
                body.vr *= Math.pow(0.994, dt * 60);

                var speedCap = body.depth === 'near' ? -34 : body.depth === 'mid' ? -28 : -18;
                body.vx = clamp(body.vx, body.wind * 1.35, speedCap);
                body.vy = clamp(body.vy, -22, 22);
                body.vr = clamp(body.vr, -28, 28);

                body.x += body.vx * dt;
                body.y += body.vy * dt;
                body.rot += body.vr * dt;
                body.rot += body.vx * dt * 0.015;

                if (body.y < height * 0.02) {
                    body.y = height * 0.02;
                    body.vy = Math.abs(body.vy) * 0.35;
                }
                if (body.y > height - body.size * 0.2) {
                    body.y = height - body.size * 0.2;
                    body.vy = -Math.abs(body.vy) * 0.4;
                }

                if (body.x < -body.size * 1.5) {
                    body.x = width + rand(60, 220);
                    body.preferredY = rand(height * 0.12, height * 0.7);
                    body.y = body.preferredY;
                    body.vx = rand(body.cfg.wind[0], body.cfg.wind[1]) / body.mass;
                    body.wind = body.vx * body.mass;
                    body.vy = rand(-6, 6) / body.mass;
                    body.rot = rand(-8, 8);
                    body.enter = 0;
                    body.baseOpacity = rand(
                        body.cfg.opacity[0],
                        body.cfg.opacity[1]
                    );
                }
            }

            for (i = 0; i < bodies.length; i += 1) {
                for (j = i + 1; j < bodies.length; j += 1) {
                    softCollide(bodies[i], bodies[j]);
                }
            }

            for (i = 0; i < bodies.length; i += 1) {
                body = bodies[i];
                var centerX = body.x + body.size * 0.5;
                var focus = 1 - Math.min(1, Math.abs(centerX - width * 0.5) / (width * 0.48));
                focus = focus * focus;
                var scale = 0.92 + focus * 0.16;
                var depthParallax = body.depth === 'near' ? 1 : body.depth === 'mid' ? 0.55 : 0.28;
                var ox = px * depthParallax;
                var oy = py * depthParallax;
                var opacity = body.baseOpacity * (0.72 + focus * 0.35) * body.enter;

                body.el.style.transform =
                    'translate3d(' +
                    (body.x + ox).toFixed(2) +
                    'px,' +
                    (body.y + oy).toFixed(2) +
                    'px,0) rotate(' +
                    body.rot.toFixed(2) +
                    'deg) scale(' +
                    scale.toFixed(3) +
                    ')';
                body.el.style.opacity = String(clamp(opacity, 0, 1));
                body.el.classList.toggle('is-focus', focus > 0.55);
            }
        }

        function frame(ts) {
            if (!running) return;
            if (!lastTs) lastTs = ts;
            var dt = clamp((ts - lastTs) / 1000, 0.001, 0.033);
            lastTs = ts;
            step(dt);
            rafId = window.requestAnimationFrame(frame);
        }

        function start() {
            if (running) return;
            measure();
            if (!bodies.length) resetBodies(true);
            root.classList.add('is-inview');
            running = true;
            lastTs = 0;
            rafId = window.requestAnimationFrame(frame);
        }

        function stop() {
            running = false;
            if (rafId) window.cancelAnimationFrame(rafId);
            rafId = 0;
        }

        var resizeTimer = 0;
        window.addEventListener('resize', function () {
            window.clearTimeout(resizeTimer);
            resizeTimer = window.setTimeout(function () {
                measure();
                resetBodies(false);
            }, 140);
        });

        root.addEventListener('pointermove', function (event) {
            var rect = root.getBoundingClientRect();
            hasPointer = true;
            pointer.tx = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
            pointer.ty = ((event.clientY - rect.top) / rect.height - 0.5) * 2;
        });

        root.addEventListener('pointerleave', function () {
            hasPointer = false;
            pointer.tx = 0;
            pointer.ty = 0;
        });

        if ('IntersectionObserver' in window) {
            var observer = new IntersectionObserver(
                function (entries) {
                    entries.forEach(function (entry) {
                        if (entry.isIntersecting) start();
                        else stop();
                    });
                },
                { threshold: 0.18 }
            );
            observer.observe(root);
        } else {
            start();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWelcomeFloat);
    } else {
        initWelcomeFloat();
    }
})();
