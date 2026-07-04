"""Floating recording indicator: a small rounded panel with a live waveform,
shown while the push-to-talk chord is held. Pure AppKit via pyobjc."""
import collections

import objc
from AppKit import (
    NSBackingStoreBuffered,
    NSBezierPath,
    NSColor,
    NSPanel,
    NSScreen,
    NSTimer,
    NSView,
    NSWindowStyleMaskBorderless,
    NSWindowStyleMaskNonactivatingPanel,
)

BAR_COUNT = 24
PANEL_W, PANEL_H = 260, 56


class WaveView(NSView):
    def initWithFrame_(self, frame):
        self = objc.super(WaveView, self).initWithFrame_(frame)
        if self is None:
            return None
        self.levels = collections.deque([0.02] * BAR_COUNT, maxlen=BAR_COUNT)
        return self

    def drawRect_(self, rect):
        b = self.bounds()
        NSColor.colorWithCalibratedWhite_alpha_(0.08, 0.88).setFill()
        NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(b, 16, 16).fill()
        pad, gap = 16, 3
        bw = (b.size.width - 2 * pad - gap * (BAR_COUNT - 1)) / BAR_COUNT
        NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.62, 0.15, 1.0).setFill()
        for i, lv in enumerate(self.levels):
            bh = max(4, min(1.0, lv * 10) * (b.size.height - 22))
            x = pad + i * (bw + gap)
            y = (b.size.height - bh) / 2
            NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                ((x, y), (bw, bh)), bw / 2, bw / 2
            ).fill()


class Overlay:
    """show()/hide() must be called on the main thread (use AppHelper.callAfter)."""

    def __init__(self, level_fn):
        self.level_fn = level_fn
        screen = NSScreen.mainScreen().frame()
        x = (screen.size.width - PANEL_W) / 2
        self.panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            ((x, 110), (PANEL_W, PANEL_H)),
            NSWindowStyleMaskBorderless | NSWindowStyleMaskNonactivatingPanel,
            NSBackingStoreBuffered,
            False,
        )
        self.panel.setLevel_(25)  # above normal windows (status level)
        self.panel.setOpaque_(False)
        self.panel.setBackgroundColor_(NSColor.clearColor())
        self.panel.setIgnoresMouseEvents_(True)
        self.panel.setCollectionBehavior_(1)  # visible on all Spaces
        self.view = WaveView.alloc().initWithFrame_(((0, 0), (PANEL_W, PANEL_H)))
        self.panel.setContentView_(self.view)
        self._timer = None

    def _tick(self, _timer):
        self.view.levels.append(self.level_fn())
        self.view.setNeedsDisplay_(True)

    def show(self):
        self.view.levels.extend([0.02] * BAR_COUNT)
        self.panel.orderFrontRegardless()
        self._timer = NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
            1 / 30.0, True, self._tick
        )

    def hide(self):
        if self._timer is not None:
            self._timer.invalidate()
            self._timer = None
        self.panel.orderOut_(None)
