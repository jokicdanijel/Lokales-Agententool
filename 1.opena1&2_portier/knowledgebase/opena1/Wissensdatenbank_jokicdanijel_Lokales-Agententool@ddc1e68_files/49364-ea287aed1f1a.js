(globalThis.webpackChunk_github_ui_github_ui =
  globalThis.webpackChunk_github_ui_github_ui || []).push([
  [16769, 49364],
  {
    6907: (e, t, n) => {
      "use strict";
      n.d(t, { x: () => s });
      var r = n(2642),
        i = n(50622);
      function s(e, t) {
        let n = (0, r.a)(e);
        if (isNaN(n.getTime())) throw RangeError("Invalid time value");
        let s = t?.format ?? "extended",
          o = t?.representation ?? "complete",
          a = "",
          l = "",
          u = "extended" === s ? "-" : "";
        if ("time" !== o) {
          let e = (0, i.F)(n.getDate(), 2),
            t = (0, i.F)(n.getMonth() + 1, 2),
            r = (0, i.F)(n.getFullYear(), 4);
          a = `${r}${u}${t}${u}${e}`;
        }
        if ("date" !== o) {
          let e = n.getTimezoneOffset();
          if (0 !== e) {
            let t = Math.abs(e),
              n = (0, i.F)(Math.trunc(t / 60), 2),
              r = (0, i.F)(t % 60, 2);
            l = `${e < 0 ? "+" : "-"}${n}:${r}`;
          } else l = "Z";
          let t = (0, i.F)(n.getHours(), 2),
            r = (0, i.F)(n.getMinutes(), 2),
            o = (0, i.F)(n.getSeconds(), 2),
            u = "" === a ? "" : "T",
            c = [t, r, o].join("extended" === s ? ":" : "");
          a = `${a}${u}${c}${l}`;
        }
        return a;
      }
    },
    9802: (e, t, n) => {
      "use strict";
      n.d(t, { e: () => i });
      var r = n(83592);
      function i(e) {
        return (0, r.s)(e, Date.now());
      }
    },
    10436: (e, t, n) => {
      "use strict";
      n.d(t, { lG: () => g, m4: () => v, jl: () => c });
      var r = n(1481),
        i = n(49539),
        s = n(38267),
        o = n(96540),
        a = n(74848);
      let l = (0, s.Ay)(r.A)
          .withConfig({ shouldForwardProp: (e) => "sx" !== e })
          .withConfig({
            displayName: "TabNav__StyledTabNav",
            componentId: "sc-13kad3t-0",
          })(["", ""], i.A),
        u = (0, s.Ay)(r.A.Link)
          .withConfig({ shouldForwardProp: (e) => "sx" !== e })
          .withConfig({
            displayName: "TabNav__StyledTabNavLink",
            componentId: "sc-13kad3t-1",
          })(["", ""], i.A),
        c = Object.assign(
          ({ as: e, ...t }) =>
            (0, a.jsx)(l, { ...t, ...(e ? { forwardedAs: e } : {}) }),
          {
            Link: (0, o.forwardRef)(({ as: e, ...t }, n) =>
              (0, a.jsx)(u, { ...t, ...(e ? { forwardedAs: e } : {}), ref: n }),
            ),
          },
        );
      var d = n(29e3),
        h = n(45846);
      let p = (0, o.forwardRef)(function (e, t) {
          return (0, a.jsx)(h.A, { as: d.A, ref: t, ...e });
        }),
        f = (0, o.forwardRef)(({ as: e, ...t }, n) =>
          (0, a.jsx)(p, { ...t, ...(e ? { forwardedAs: e } : {}), ref: n }),
        ),
        m = (0, o.forwardRef)(function (e, t) {
          return (0, a.jsx)(h.A, { as: d.A.Header, ref: t, ...e });
        }),
        g = Object.assign(f, {
          Header: (0, o.forwardRef)(({ as: e, ...t }, n) =>
            (0, a.jsx)(m, { ...t, ...(e ? { forwardedAs: e } : {}), ref: n }),
          ),
        });
      var _ = n(10095);
      let y = (0, s.Ay)(_.A)
          .withConfig({ shouldForwardProp: (e) => "sx" !== e })
          .withConfig({
            displayName: "Octicon__StyledOcticon",
            componentId: "sc-jtj3m8-0",
          })(["", ""], ({ color: e, sx: t }) =>
          (0, i.A)({ sx: { color: e, ...t } }),
        ),
        v = (0, o.forwardRef)(({ as: e, ...t }, n) =>
          (0, a.jsx)(y, { ...t, ...(e ? { forwardedAs: e } : {}), ref: n }),
        );
      var w = n(55255);
      let b = (0, s.Ay)(w.A)
          .withConfig({ shouldForwardProp: (e) => "sx" !== e })
          .withConfig({
            displayName: "Tooltip__StyledTooltip",
            componentId: "sc-145jcib-0",
          })(["", ""], i.A),
        E = (0, o.forwardRef)(function ({ as: e, ...t }, n) {
          return (0, a.jsx)(b, {
            ...t,
            ...(e ? { forwardedAs: e } : {}),
            ref: n,
          });
        });
      ((E.alignments = w.A.alignments),
        (E.directions = w.A.directions),
        (E.__SLOT__ = w.A.__SLOT__));
      var x = n(9470);
      let C = (0, o.forwardRef)(function (e, t) {
          return (0, a.jsx)(h.A, { as: x.l, ref: t, ...e });
        }),
        O = (0, s.Ay)(x.l.Item)
          .withConfig({ shouldForwardProp: (e) => "sx" !== e })
          .withConfig({
            displayName: "ActionList__StyledActionListItem",
            componentId: "sc-1ugfmds-0",
          })(["", ""], i.A);
      Object.assign(C, {
        Item: (0, o.forwardRef)(({ as: e, ...t }, n) =>
          (0, a.jsx)(O, { ...t, ...(e ? { forwardedAs: e } : {}), ref: n }),
        ),
        Group: function (e) {
          return (0, a.jsx)(h.A, { as: x.l.Group, ...e });
        },
        Divider: function (e) {
          return (0, a.jsx)(h.A, { as: x.l.Divider, ...e });
        },
      });
    },
    24249: (e, t, n) => {
      "use strict";
      n.d(t, { Qr: () => InputRange });
      let InputStyleCloneUpdateEvent = class InputStyleCloneUpdateEvent extends Event {
        constructor() {
          super("update");
        }
      };
      let r = new WeakMap();
      let InputStyleClone = class InputStyleClone extends EventTarget {
        #e = new MutationObserver(() => this.#t());
        #n = new ResizeObserver(() => this.#r());
        #i;
        #s = document.createElement("div");
        #o = document.createElement("div");
        static for(e) {
          let t = r.get(e);
          return (t || ((t = new InputStyleClone(e)), r.set(e, t)), t);
        }
        constructor(e) {
          (super(),
            (this.#i = new WeakRef(e)),
            (this.#s.style.position = "absolute"),
            (this.#s.style.pointerEvents = "none"),
            this.#s.setAttribute("aria-hidden", "true"),
            this.#s.appendChild(this.#o),
            (this.#o.style.pointerEvents = "none"),
            (this.#o.style.userSelect = "none"),
            (this.#o.style.overflow = "hidden"),
            (this.#o.style.display = "block"),
            (this.#o.style.visibility = "hidden"),
            e instanceof HTMLTextAreaElement
              ? ((this.#o.style.whiteSpace = "pre-wrap"),
                (this.#o.style.wordWrap = "break-word"))
              : ((this.#o.style.whiteSpace = "nowrap"),
                (this.#o.style.display = "table-cell"),
                (this.#o.style.verticalAlign = "middle")),
            e.after(this.#s),
            this.#t(),
            this.#a(),
            this.#e.observe(e, { attributeFilter: ["style", "dir"] }),
            this.#n.observe(e),
            document.addEventListener("scroll", this.#l, { capture: !0 }),
            window.addEventListener("resize", this.#l, { capture: !0 }),
            e.addEventListener("input", this.#u, { capture: !0 }));
        }
        get element() {
          return this.#o;
        }
        forceUpdate() {
          (this.#t(), this.#a());
        }
        disconnect() {
          (this.#s?.remove(),
            this.#e.disconnect(),
            this.#n.disconnect(),
            document.removeEventListener("scroll", this.#l, { capture: !0 }),
            window.removeEventListener("resize", this.#l, { capture: !0 }));
          let e = this.#c;
          e &&
            (e.removeEventListener("input", this.#u, { capture: !0 }),
            r.delete(e));
        }
        get #c() {
          return this.#i?.deref();
        }
        #d(e) {
          let t = this.#c;
          return t ? e(t) : this.disconnect();
        }
        #h = 0;
        #p = 0;
        #f() {
          this.#d((e) => {
            let t = window.getComputedStyle(e);
            ((this.#o.style.height = t.height),
              (this.#o.style.width = t.width),
              e.clientHeight !== this.#o.clientHeight &&
                (this.#o.style.height = `calc(${t.height} + ${e.clientHeight - this.#o.clientHeight}px)`),
              e.clientWidth !== this.#o.clientWidth &&
                (this.#o.style.width = `calc(${t.width} + ${e.clientWidth - this.#o.clientWidth}px)`));
            let n = e.getBoundingClientRect(),
              r = this.#o.getBoundingClientRect();
            ((this.#h = this.#h + n.left - r.left),
              (this.#p = this.#p + n.top - r.top),
              (this.#o.style.transform = `translate(${this.#h}px, ${this.#p}px)`),
              (this.#o.scrollTop = e.scrollTop),
              (this.#o.scrollLeft = e.scrollLeft),
              this.dispatchEvent(new InputStyleCloneUpdateEvent()));
          });
        }
        #m = !1;
        #r() {
          this.#m ||
            ((this.#m = !0),
            requestAnimationFrame(() => {
              (this.#f(), (this.#m = !1));
            }));
        }
        #t() {
          this.#d((e) => {
            let t = window.getComputedStyle(e);
            for (let e of i) this.#o.style[e] = t[e];
            this.#r();
          });
        }
        #a() {
          this.#d((e) => {
            ((this.#o.textContent = e.value), this.#f());
          });
        }
        #u = () => this.#a();
        #l = (e) => {
          this.#d((t) => {
            (e.target === document ||
              e.target === window ||
              (e.target instanceof Node && e.target.contains(t))) &&
              this.#r();
          });
        };
      };
      let i = [
        "direction",
        "writingMode",
        "unicodeBidi",
        "textOrientation",
        "boxSizing",
        "borderTopWidth",
        "borderRightWidth",
        "borderBottomWidth",
        "borderLeftWidth",
        "borderStyle",
        "paddingTop",
        "paddingRight",
        "paddingBottom",
        "paddingLeft",
        "fontStyle",
        "fontVariant",
        "fontWeight",
        "fontStretch",
        "fontSize",
        "fontSizeAdjust",
        "lineHeight",
        "fontFamily",
        "textAlign",
        "textTransform",
        "textIndent",
        "textDecoration",
        "letterSpacing",
        "wordSpacing",
        "tabSize",
        "MozTabSize",
      ];
      let InputRange = class InputRange {
        #g;
        #_;
        #y;
        constructor(e, t = 0, n = t) {
          ((this.#g = e), (this.#_ = t), (this.#y = n));
        }
        static fromSelection(e) {
          let { selectionStart: t, selectionEnd: n } = e;
          return new InputRange(e, t ?? void 0, n ?? void 0);
        }
        get collapsed() {
          return this.startOffset === this.endOffset;
        }
        get commonAncestorContainer() {
          return this.#g;
        }
        get endContainer() {
          return this.#g;
        }
        get startContainer() {
          return this.#g;
        }
        get startOffset() {
          return this.#_;
        }
        get endOffset() {
          return this.#y;
        }
        setStartOffset(e) {
          this.#_ = this.#v(e);
        }
        setEndOffset(e) {
          this.#y = this.#v(e);
        }
        collapse(e = !1) {
          e
            ? this.setEndOffset(this.startOffset)
            : this.setStartOffset(this.endOffset);
        }
        cloneContents() {
          return this.#w().cloneContents();
        }
        cloneRange() {
          return new InputRange(this.#g, this.startOffset, this.endOffset);
        }
        getBoundingClientRect() {
          return this.#w().getBoundingClientRect();
        }
        getClientRects() {
          return this.#w().getClientRects();
        }
        toString() {
          return this.#w().toString();
        }
        getStyleClone() {
          return this.#b;
        }
        get #b() {
          return InputStyleClone.for(this.#g);
        }
        get #o() {
          return this.#b;
        }
        #v(e) {
          return Math.max(0, Math.min(e, this.#g.value.length));
        }
        #w() {
          let e = document.createRange(),
            t = this.#o.element.childNodes[0];
          return (
            t && (e.setStart(t, this.startOffset), e.setEnd(t, this.endOffset)),
            e
          );
        }
      };
    },
    31993: (e, t, n) => {
      "use strict";
      function r(e) {
        return e;
      }
      n.d(t, { j: () => r });
    },
    34052: (e, t, n) => {
      "use strict";
      var r = n(9963),
        i = n(41241),
        s = n(90007).loadQuery,
        o = n(13635),
        a = n(50456),
        l = n(40121),
        u = n(7360),
        c = n(73720),
        d = n(42695),
        h = n(15940),
        p = n(39420),
        f = n(6505),
        m = n(71517),
        g = n(7058),
        _ = n(53386),
        y = n(91529),
        v = n(69487);
      e.exports = {
        ConnectionHandler: v.ConnectionHandler,
        applyOptimisticMutation: v.applyOptimisticMutation,
        commitLocalUpdate: v.commitLocalUpdate,
        commitMutation: v.commitMutation,
        graphql: v.graphql,
        readInlineData: v.readInlineData,
        requestSubscription: v.requestSubscription,
        EntryPointContainer: r,
        RelayEnvironmentProvider: a,
        ProfilerContext: o,
        fetchQuery: v.fetchQuery,
        loadQuery: s,
        loadEntryPoint: i,
        useFragment: u,
        useLazyLoadQuery: c,
        useEntryPointLoader: l,
        useQueryLoader: f,
        useMutation: d,
        usePaginationFragment: h,
        usePreloadedQuery: p,
        useRefetchableFragment: m,
        useRelayEnvironment: g,
        useSubscribeToInvalidationState: _,
        useSubscription: y,
      };
    },
    34784: (e, t, n) => {
      e.exports = n(34052);
    },
    46996: (e, t, n) => {
      "use strict";
      n.d(t, { A: () => i });
      var r = n(21179);
      let i = function (e, t) {
        return (0, r.A)(e, t);
      };
    },
    47990: (e, t, n) => {
      "use strict";
      function r(e, t, n) {
        return Math.min(Math.max(e, n), t);
      }
      n.d(t, { BT: () => m, Du: () => i });
      let ColorError = class ColorError extends Error {
        constructor(e) {
          super(`Failed to parse color: "${e}"`);
        }
      };
      function i(e) {
        if ("string" != typeof e) throw new ColorError(e);
        if ("transparent" === e.trim().toLowerCase()) return [0, 0, 0, 0];
        let t = e.trim();
        t = h.test(e)
          ? (function (e) {
              let t =
                o[
                  (function (e) {
                    let t = 5381,
                      n = e.length;
                    for (; n; ) t = (33 * t) ^ e.charCodeAt(--n);
                    return (t >>> 0) % 2341;
                  })(e.toLowerCase().trim())
                ];
              if (!t) throw new ColorError(e);
              return `#${t}`;
            })(e)
          : e;
        let n = l.exec(t);
        if (n) {
          let e = Array.from(n).slice(1);
          return [
            ...e.slice(0, 3).map((e) => parseInt(a(e, 2), 16)),
            parseInt(a(e[3] || "f", 2), 16) / 255,
          ];
        }
        let i = u.exec(t);
        if (i) {
          let e = Array.from(i).slice(1);
          return [
            ...e.slice(0, 3).map((e) => parseInt(e, 16)),
            parseInt(e[3] || "ff", 16) / 255,
          ];
        }
        let s = c.exec(t);
        if (s) {
          let e = Array.from(s).slice(1);
          return [
            ...e.slice(0, 3).map((e) => parseInt(e, 10)),
            parseFloat(e[3] || "1"),
          ];
        }
        let p = d.exec(t);
        if (p) {
          let [t, n, i, s] = Array.from(p).slice(1).map(parseFloat);
          if (r(0, 100, n) !== n || r(0, 100, i) !== i) throw new ColorError(e);
          return [...f(t, n, i), Number.isNaN(s) ? 1 : s];
        }
        throw new ColorError(e);
      }
      let s = (e) => parseInt(e.replace(/_/g, ""), 36),
        o =
          "1q29ehhb 1n09sgk7 1kl1ekf_ _yl4zsno 16z9eiv3 1p29lhp8 _bd9zg04 17u0____ _iw9zhe5 _to73___ _r45e31e _7l6g016 _jh8ouiv _zn3qba8 1jy4zshs 11u87k0u 1ro9yvyo 1aj3xael 1gz9zjz0 _3w8l4xo 1bf1ekf_ _ke3v___ _4rrkb__ 13j776yz _646mbhl _nrjr4__ _le6mbhl 1n37ehkb _m75f91n _qj3bzfz 1939yygw 11i5z6x8 _1k5f8xs 1509441m 15t5lwgf _ae2th1n _tg1ugcv 1lp1ugcv 16e14up_ _h55rw7n _ny9yavn _7a11xb_ 1ih442g9 _pv442g9 1mv16xof 14e6y7tu 1oo9zkds 17d1cisi _4v9y70f _y98m8kc 1019pq0v 12o9zda8 _348j4f4 1et50i2o _8epa8__ _ts6senj 1o350i2o 1mi9eiuo 1259yrp0 1ln80gnw _632xcoy 1cn9zldc _f29edu4 1n490c8q _9f9ziet 1b94vk74 _m49zkct 1kz6s73a 1eu9dtog _q58s1rz 1dy9sjiq __u89jo3 _aj5nkwg _ld89jo3 13h9z6wx _qa9z2ii _l119xgq _bs5arju 1hj4nwk9 1qt4nwk9 1ge6wau6 14j9zlcw 11p1edc_ _ms1zcxe _439shk6 _jt9y70f _754zsow 1la40eju _oq5p___ _x279qkz 1fa5r3rv _yd2d9ip _424tcku _8y1di2_ _zi2uabw _yy7rn9h 12yz980_ __39ljp6 1b59zg0x _n39zfzp 1fy9zest _b33k___ _hp9wq92 1il50hz4 _io472ub _lj9z3eo 19z9ykg0 _8t8iu3a 12b9bl4a 1ak5yw0o _896v4ku _tb8k8lv _s59zi6t _c09ze0p 1lg80oqn 1id9z8wb _238nba5 1kq6wgdi _154zssg _tn3zk49 _da9y6tc 1sg7cv4f _r12jvtt 1gq5fmkz 1cs9rvci _lp9jn1c _xw1tdnb 13f9zje6 16f6973h _vo7ir40 _bt5arjf _rc45e4t _hr4e100 10v4e100 _hc9zke2 _w91egv_ _sj2r1kk 13c87yx8 _vqpds__ _ni8ggk8 _tj9yqfb 1ia2j4r4 _7x9b10u 1fc9ld4j 1eq9zldr _5j9lhpx _ez9zl6o _md61fzm"
            .split(" ")
            .reduce((e, t) => {
              let n = s(t.substring(0, 3)),
                r = s(t.substring(3)).toString(16),
                i = "";
              for (let e = 0; e < 6 - r.length; e++) i += "0";
              return ((e[n] = `${i}${r}`), e);
            }, {}),
        a = (e, t) =>
          Array.from(Array(t))
            .map(() => e)
            .join(""),
        l = RegExp(`^#${a("([a-f0-9])", 3)}([a-f0-9])?$`, "i"),
        u = RegExp(`^#${a("([a-f0-9]{2})", 3)}([a-f0-9]{2})?$`, "i"),
        c = RegExp(
          `^rgba?\\(\\s*(\\d+)\\s*${a(",\\s*(\\d+)\\s*", 2)}(?:,\\s*([\\d.]+))?\\s*\\)$`,
          "i",
        ),
        d =
          /^hsla?\(\s*([\d.]+)\s*,\s*([\d.]+)%\s*,\s*([\d.]+)%(?:\s*,\s*([\d.]+))?\s*\)$/i,
        h = /^[a-z]+$/i,
        p = (e) => Math.round(255 * e),
        f = (e, t, n) => {
          let r = n / 100;
          if (0 === t) return [r, r, r].map(p);
          let i = (((e % 360) + 360) % 360) / 60,
            s = (t / 100) * (1 - Math.abs(2 * r - 1)),
            o = s * (1 - Math.abs((i % 2) - 1)),
            a = 0,
            l = 0,
            u = 0;
          i >= 0 && i < 1
            ? ((a = s), (l = o))
            : i >= 1 && i < 2
              ? ((a = o), (l = s))
              : i >= 2 && i < 3
                ? ((l = s), (u = o))
                : i >= 3 && i < 4
                  ? ((l = o), (u = s))
                  : i >= 4 && i < 5
                    ? ((a = o), (u = s))
                    : i >= 5 && i < 6 && ((a = s), (u = o));
          let c = r - s / 2;
          return [a + c, l + c, u + c].map(p);
        };
      function m(e) {
        let [t, n, r, s] = i(e).map((e, t) => (3 === t ? e : e / 255)),
          o = Math.max(t, n, r),
          a = Math.min(t, n, r),
          l = (o + a) / 2;
        if (o === a) return [0, 0, l, s];
        let u = o - a;
        return [
          60 *
            (t === o
              ? (n - r) / u + 6 * (n < r)
              : n === o
                ? (r - t) / u + 2
                : (t - n) / u + 4),
          l > 0.5 ? u / (2 - o - a) : u / (o + a),
          l,
          s,
        ];
      }
    },
    61388: (e, t, n) => {
      "use strict";
      n.d(t, { _: () => a });
      var r = n(36158),
        i = n(26261),
        s = n(66500),
        o = n(24880),
        a = class extends s.Q {
          #E;
          #x = void 0;
          #C;
          #O;
          constructor(e, t) {
            (super(),
              (this.#E = e),
              this.setOptions(t),
              this.bindMethods(),
              this.#A());
          }
          bindMethods() {
            ((this.mutate = this.mutate.bind(this)),
              (this.reset = this.reset.bind(this)));
          }
          setOptions(e) {
            let t = this.options;
            ((this.options = this.#E.defaultMutationOptions(e)),
              (0, o.f8)(this.options, t) ||
                this.#E
                  .getMutationCache()
                  .notify({
                    type: "observerOptionsUpdated",
                    mutation: this.#C,
                    observer: this,
                  }),
              t?.mutationKey &&
              this.options.mutationKey &&
              (0, o.EN)(t.mutationKey) !== (0, o.EN)(this.options.mutationKey)
                ? this.reset()
                : this.#C?.state.status === "pending" &&
                  this.#C.setOptions(this.options));
          }
          onUnsubscribe() {
            this.hasListeners() || this.#C?.removeObserver(this);
          }
          onMutationUpdate(e) {
            (this.#A(), this.#S(e));
          }
          getCurrentResult() {
            return this.#x;
          }
          reset() {
            (this.#C?.removeObserver(this),
              (this.#C = void 0),
              this.#A(),
              this.#S());
          }
          mutate(e, t) {
            return (
              (this.#O = t),
              this.#C?.removeObserver(this),
              (this.#C = this.#E
                .getMutationCache()
                .build(this.#E, this.options)),
              this.#C.addObserver(this),
              this.#C.execute(e)
            );
          }
          #A() {
            let e = this.#C?.state ?? (0, r.$)();
            this.#x = {
              ...e,
              isPending: "pending" === e.status,
              isSuccess: "success" === e.status,
              isError: "error" === e.status,
              isIdle: "idle" === e.status,
              mutate: this.mutate,
              reset: this.reset,
            };
          }
          #S(e) {
            i.jG.batch(() => {
              if (this.#O && this.hasListeners()) {
                let t = this.#x.variables,
                  n = this.#x.context,
                  r = {
                    client: this.#E,
                    meta: this.options.meta,
                    mutationKey: this.options.mutationKey,
                  };
                e?.type === "success"
                  ? (this.#O.onSuccess?.(e.data, t, n, r),
                    this.#O.onSettled?.(e.data, null, t, n, r))
                  : e?.type === "error" &&
                    (this.#O.onError?.(e.error, t, n, r),
                    this.#O.onSettled?.(void 0, e.error, t, n, r));
              }
              this.listeners.forEach((e) => {
                e(this.#x);
              });
            });
          }
        };
    },
    66661: (e, t, n) => {
      "use strict";
      function r(e) {
        let t = e.parentNode;
        if (null === t || !(t instanceof HTMLElement)) throw Error();
        let n = 0;
        t instanceof HTMLOListElement && 1 !== t.start && (n = t.start - 1);
        let r = t.children;
        for (let t = 0; t < r.length; ++t) if (r[t] === e) return n + t;
        return n;
      }
      n.d(t, { P: () => Quote, g: () => MarkdownQuote });
      let i = 0;
      function s(e) {
        return e
          .replace(/&/g, "&amp;")
          .replace(/'/g, "&apos;")
          .replace(/"/g, "&quot;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;");
      }
      let o = {
        INPUT: (e) =>
          e instanceof HTMLInputElement && e.checked ? "[x] " : "[ ] ",
        CODE(e) {
          let t = e.textContent || "";
          return e.parentNode && "PRE" === e.parentNode.nodeName
            ? ((e.textContent = `\`\`\`
${t.replace(/\n+$/, "")}
\`\`\`

`),
              e)
            : t.indexOf("`") >= 0
              ? `\`\` ${t} \`\``
              : `\`${t}\``;
        },
        P(e) {
          let t = document.createElement("p");
          return (
            (t.textContent = (e.textContent || "").replace(
              /<(\/?)(pre|strong|weak|em)>/g,
              "\\<$1$2\\>",
            )),
            t
          );
        },
        STRONG: (e) => `**${e.textContent || ""}**`,
        EM: (e) => `_${e.textContent || ""}_`,
        DEL: (e) => `~${e.textContent || ""}~`,
        BLOCKQUOTE(e) {
          let t = (e.textContent || "").trim().replace(/^/gm, "> "),
            n = document.createElement("pre");
          return (
            (n.textContent = `${t}

`),
            n
          );
        },
        A(e) {
          let t = e.textContent || "",
            n = e.getAttribute("href");
          return /^https?:/.test(t) && t === n ? t : n ? `[${t}](${n})` : t;
        },
        IMG(e) {
          let t = e.getAttribute("alt") || "",
            n = e.getAttribute("src");
          if (!n) throw Error();
          let r = e.hasAttribute("width")
              ? ` width="${s(e.getAttribute("width") || "")}"`
              : "",
            i = e.hasAttribute("height")
              ? ` height="${s(e.getAttribute("height") || "")}"`
              : "";
          return r || i
            ? `<img alt="${s(t)}"${r}${i} src="${s(n)}">`
            : `![${t}](${n})`;
        },
        LI(e) {
          let t,
            n,
            s = e.parentNode;
          if (!s) throw Error();
          let o = "";
          if (
            ((t = e.childNodes[0]),
            (n = e.childNodes[1]),
            !t ||
              !(e.childNodes.length < 3) ||
              ("OL" !== t.nodeName && "UL" !== t.nodeName) ||
              (n &&
                (n.nodeType !== Node.TEXT_NODE ||
                  (n.textContent || "").trim())))
          )
            if ("OL" === s.nodeName)
              if (i > 0 && !s.previousSibling) {
                let t = r(e) + i + 1;
                o = `${t}\\. `;
              } else o = `${r(e) + 1}. `;
            else o = "* ";
          let a = o.replace(/\S/g, " "),
            l = (e.textContent || "").trim().replace(/^/gm, a),
            u = document.createElement("pre");
          return ((u.textContent = l.replace(a, o)), u);
        },
        OL(e) {
          let t = document.createElement("li");
          return (t.appendChild(document.createElement("br")), e.append(t), e);
        },
        H1(e) {
          let t = parseInt(e.nodeName.slice(1));
          return (e.prepend(`${Array(t + 1).join("#")} `), e);
        },
        UL: (e) => e,
      };
      o.UL = o.OL;
      for (let e = 2; e <= 6; ++e) o[`H${e}`] = o.H1;
      let Quote = class Quote {
        constructor() {
          ((this.selection = window.getSelection()),
            (this.processSelectionText = (e) => e));
        }
        closest(e) {
          let t = this.range.startContainer,
            n = t instanceof Element ? t : t.parentElement;
          return n ? n.closest(e) : null;
        }
        get active() {
          var e;
          return (
            ((null == (e = this.selection) ? void 0 : e.rangeCount) || 0) > 0
          );
        }
        get range() {
          var e;
          return (null == (e = this.selection) ? void 0 : e.rangeCount)
            ? this.selection.getRangeAt(0)
            : new Range();
        }
        set range(e) {
          var t, n;
          (null == (t = this.selection) || t.removeAllRanges(),
            null == (n = this.selection) || n.addRange(e));
        }
        set processSelectionTextFn(e) {
          this.processSelectionText = e;
        }
        get selectionText() {
          var e;
          return this.processSelectionText(
            (null == (e = this.selection) ? void 0 : e.toString().trim()) || "",
          );
        }
        get quotedText() {
          return `> ${this.selectionText.replace(
            /\n/g,
            `
> `,
          )}

`;
        }
        select(e) {
          this.selection &&
            (this.selection.removeAllRanges(),
            this.selection.selectAllChildren(e));
        }
        insert(e) {
          (e.value
            ? (e.value = `${e.value}

${this.quotedText}`)
            : (e.value = this.quotedText),
            e.dispatchEvent(
              new CustomEvent("change", { bubbles: !0, cancelable: !1 }),
            ),
            e.focus(),
            (e.selectionStart = e.value.length),
            (e.scrollTop = e.scrollHeight));
        }
      };
      let MarkdownQuote = class MarkdownQuote extends Quote {
        constructor(e = "", t) {
          (super(), (this.scopeSelector = e), (this.callback = t));
        }
        get selectionText() {
          var e, t;
          if (!this.selection) return "";
          let n = (function (e, t) {
            let n = e.startContainer;
            if (!n || !n.parentNode || !(n.parentNode instanceof HTMLElement))
              throw Error("the range must start within an HTMLElement");
            let s = n.parentNode,
              o = e.cloneContents();
            if (t) {
              let e = o.querySelector(t);
              e && (o = document.createDocumentFragment()).appendChild(e);
            }
            i = 0;
            let a = s.closest("li");
            if (s.closest("pre")) {
              let e = document.createElement("pre");
              (e.appendChild(o),
                (o = document.createDocumentFragment()).appendChild(e));
            } else if (
              a &&
              a.parentNode &&
              ("OL" === a.parentNode.nodeName && (i = r(a)),
              !o.querySelector("li"))
            ) {
              let e = document.createElement("li");
              if (!a.parentNode) throw Error();
              let t = document.createElement(a.parentNode.nodeName);
              (e.appendChild(o),
                t.appendChild(e),
                (o = document.createDocumentFragment()).appendChild(t));
            }
            return o;
          })(this.range, null != (e = this.scopeSelector) ? e : "");
          null == (t = this.callback) || t.call(this, n);
          let s = document.createNodeIterator(n, NodeFilter.SHOW_ELEMENT, {
              acceptNode: (e) =>
                e.nodeName in o &&
                !(function (e) {
                  if (
                    e instanceof HTMLAnchorElement &&
                    1 === e.childNodes.length
                  ) {
                    let t = e.childNodes[0];
                    if (t instanceof HTMLImageElement) return t.src === e.href;
                  }
                  return !1;
                })(e) &&
                ("IMG" === e.nodeName ||
                  null != e.firstChild ||
                  ("INPUT" === e.nodeName &&
                    e instanceof HTMLInputElement &&
                    "checkbox" === e.type))
                  ? NodeFilter.FILTER_ACCEPT
                  : NodeFilter.FILTER_SKIP,
            }),
            a = [],
            l = s.nextNode();
          for (; l; )
            (l instanceof HTMLElement && a.push(l), (l = s.nextNode()));
          for (let e of (a.reverse(), a)) e.replaceWith(o[e.nodeName](e));
          let u = document.body;
          if (!u) return "";
          let c = document.createElement("div");
          (c.appendChild(n),
            (c.style.cssText = "position:absolute;left:-9999px;"),
            u.appendChild(c));
          let d = "";
          try {
            let e = document.createRange();
            (e.selectNodeContents(c),
              this.selection.removeAllRanges(),
              this.selection.addRange(e),
              (d = this.selection.toString()),
              this.selection.removeAllRanges(),
              e.detach());
          } finally {
            u.removeChild(c);
          }
          return this.processSelectionText(d.trim());
        }
      };
    },
    79639: (e, t, n) => {
      "use strict";
      n.d(t, { P: () => s });
      var r = n(85551),
        i = n(40828);
      function s(e) {
        return (0, r.r)(e, (0, i.e)(Date.now(), 1));
      }
    },
    83592: (e, t, n) => {
      "use strict";
      n.d(t, { s: () => i });
      var r = n(2642);
      function i(e, t) {
        let n = (0, r.a)(e),
          i = (0, r.a)(t);
        return n.getFullYear() === i.getFullYear();
      }
    },
    91385: (e, t, n) => {
      "use strict";
      n.d(t, { Xq: () => a, ai: () => i, fN: () => o, qA: () => l });
      var r = -1 / 0,
        i = 1 / 0;
      function s(e, t, n, i) {
        for (
          var s = e.length,
            o = t.length,
            a = e.toLowerCase(),
            l = t.toLowerCase(),
            u = (function (e) {
              for (var t = e.length, n = Array(t), r = "/", i = 0; i < t; i++) {
                var s,
                  o = e[i];
                ("/" === r
                  ? (n[i] = 0.9)
                  : "-" === r || "_" === r || " " === r
                    ? (n[i] = 0.8)
                    : "." === r
                      ? (n[i] = 0.6)
                      : (s = r).toLowerCase() === s && o.toUpperCase() === o
                        ? (n[i] = 0.7)
                        : (n[i] = 0),
                  (r = o));
              }
              return n;
            })(t, u),
            c = 0;
          c < s;
          c++
        ) {
          ((n[c] = Array(o)), (i[c] = Array(o)));
          for (var d = r, h = c === s - 1 ? -0.005 : -0.01, p = 0; p < o; p++)
            if (a[c] === l[p]) {
              var f = r;
              (c
                ? p &&
                  (f = Math.max(i[c - 1][p - 1] + u[p], n[c - 1][p - 1] + 1))
                : (f = -0.005 * p + u[p]),
                (n[c][p] = f),
                (i[c][p] = d = Math.max(f, d + h)));
            } else ((n[c][p] = r), (i[c][p] = d += h));
        }
      }
      function o(e, t) {
        var n = e.length,
          o = t.length;
        if (!n || !o) return r;
        if (n === o) return i;
        if (o > 1024) return r;
        var a = Array(n),
          l = Array(n);
        return (s(e, t, a, l), l[n - 1][o - 1]);
      }
      function a(e, t) {
        var n = e.length,
          i = t.length,
          o = Array(n);
        if (!n || !i) return o;
        if (n === i) {
          for (var a = 0; a < n; a++) o[a] = a;
          return o;
        }
        if (i > 1024) return o;
        var l = Array(n),
          u = Array(n);
        s(e, t, l, u);
        for (var c = !1, a = n - 1, d = i - 1; a >= 0; a--)
          for (; d >= 0; d--)
            if (l[a][d] !== r && (c || l[a][d] === u[a][d])) {
              ((c = a && d && u[a][d] === l[a - 1][d - 1] + 1), (o[a] = d--));
              break;
            }
        return o;
      }
      function l(e, t) {
        ((e = e.toLowerCase()), (t = t.toLowerCase()));
        for (var n = e.length, r = 0, i = 0; r < n; r += 1)
          if (0 === (i = t.indexOf(e[r], i) + 1)) return !1;
        return !0;
      }
    },
    94747: (e, t, n) => {
      "use strict";
      n.d(t, { n: () => l });
      var r = n(96540),
        i = n(61388),
        s = n(26261),
        o = n(24880),
        a = n(97665);
      function l(e, t) {
        let n = (0, a.jE)(t),
          [l] = r.useState(() => new i._(n, e));
        r.useEffect(() => {
          l.setOptions(e);
        }, [l, e]);
        let u = r.useSyncExternalStore(
            r.useCallback((e) => l.subscribe(s.jG.batchCalls(e)), [l]),
            () => l.getCurrentResult(),
            () => l.getCurrentResult(),
          ),
          c = r.useCallback(
            (e, t) => {
              l.mutate(e, t).catch(o.lQ);
            },
            [l],
          );
        if (u.error && (0, o.GU)(l.options.throwOnError, [u.error]))
          throw u.error;
        return { ...u, mutate: c, mutateAsync: u.mutate };
      }
    },
    98107: (e, t, n) => {
      "use strict";
      n.d(t, { lG: () => r.l, zY: () => i.z, XI: () => m });
      var r = n(85203),
        i = n(65729);
      n(49716);
      var s = n(55004),
        o = n(38267),
        a = n(49539),
        l = n(74848);
      let u = (0, o.Ay)(s.A)
          .withConfig({ shouldForwardProp: (e) => "sx" !== e })
          .withConfig({
            displayName: "UnderlinePanels__StyledUnderlinePanels",
            componentId: "sc-1w35i85-0",
          })(["", ""], a.A),
        c = ({ as: e, ...t }) => (0, l.jsx)(u, { forwardedAs: e, ...t });
      ((c.displayName = "UnderlinePanels"),
        Object.assign(c, { Tab: s.A.Tab, Panel: s.A.Panel }),
        (c.__SLOT__ = s.A.__SLOT__));
      var d = n(10006);
      let { Container: h, ...p } = d.X,
        f = (0, o.Ay)(h)
          .withConfig({ shouldForwardProp: (e) => "sx" !== e })
          .withConfig({
            displayName: "DataTable__StyleDataTableContainer",
            componentId: "sc-qy1ey2-0",
          })(["", ""], a.A),
        m = Object.assign(d.X, {
          Container: function ({ as: e, ...t }) {
            return (0, l.jsx)(f, { ...t, ...(e ? { forwardedAs: e } : {}) });
          },
          ...p,
        });
    },
  },
]);
//# sourceMappingURL=49364-e30e4127887d.js.map
