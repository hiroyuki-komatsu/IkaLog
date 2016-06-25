#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import copy
import threading

import wx
import cv2

from ikalog.utils import Localization
from ikalog.ui.events import *

_ = Localization.gettext_translation('IkaUI', fallback=True).gettext

class PreviewPanel(wx.Panel):

    def SetEventHandlerEnable(self, obj, enable):
        orig_state = obj.GetEvtHandlerEnabled()
        obj.SetEvtHandlerEnabled(enable)
        return orig_state


    # IkaLog event
    def on_amarec16x10_warning(self, context, params):
        self._amarec16x10_warning = params['enabled']

    # IkaLog event
    def on_show_preview(self, context):
        self.lock.acquire()

        img = context['engine'].get('preview', context['engine']['frame'])
        self.latest_frame = cv2.resize(img, self.preview_size)

        self.refresh_at_next = True
        self.lock.release()

    # wx event
    def on_input_initialized(self, event):
        self.show_input_file((event.source == 'file'))

    # wx event
    def on_input_file_button_click(self, event):
        file_path = self.input_file_text_ctrl.GetValue()
        evt = InputFileAddedEvent(input_file=file_path)
        wx.PostEvent(self, evt)

    def show_input_file(self, show):
        self.input_file_sizer.ShowItems(show=show)
        self.Layout()

    # wx event
    def OnResize(self, event):
        w, h = self.GetClientSizeTuple()
        new_height = int((w * 720) / 1280)

        orig_state = self.SetEventHandlerEnable(self, False)
        self.SetSize((w, new_height))
        self.SetEventHandlerEnable(self, orig_state)

    # wx event
    def OnPaint(self, event):
        self.lock.acquire()
        if self.latest_frame is None:
            self.lock.release()
            return

        rect = self.preview_panel.GetRect()
        width, height = self.preview_size

        frame_rgb = cv2.cvtColor(self.latest_frame, cv2.COLOR_BGR2RGB)
        self.lock.release()

        try:
            bmp = wx.Bitmap.FromBuffer(width, height, frame_rgb)
        except:
            bmp = wx.BitmapFromBuffer(width, height, frame_rgb)

        dc = wx.BufferedPaintDC(self)
        # dc.SetBackground(wx.Brush(wx.RED))

        dc.DrawBitmap(bmp, rect.GetX(), rect.GetY())

    # wx event
    def OnTimer(self, event):
        self.lock.acquire()

        if self.latest_frame is None:
            self.lock.release()
            return

        self.lock.release()

        if not self.refresh_at_next:
            return

        if self._amarec16x10_warning is not None:
            label = self.label_amarec16x10_warning
            { True: label.Show, False: label.Hide }[self._amarec16x10_warning]()
            self._amarec16x10_warning = None

        self.Refresh()
        self.refresh_at_next = False

    def __init__(self, *args, **kwargs):
        self.refresh_at_next = False
        self.latest_frame = None
        self.lock = threading.Lock()

        wx.Panel.__init__(self, *args, **kwargs)
        self.timer = wx.Timer(self)
        self.timer.Start(100)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        self.GetTopLevelParent().Bind(EVT_INPUT_INITIALIZED,
                                      self.on_input_initialized)

        self.label_amarec16x10_warning = wx.StaticText(
            self, wx.ID_ANY, _('The image seems to be 16x10. Perhaps the source is misconfigured.'), pos=(0, 0))

        # Preview
        self.preview_size = (640, 360)
        # Spacer for the preview image.
        # This does not actually contain the preview image.
        self.preview_panel = wx.Panel(self, wx.ID_ANY, size=self.preview_size)

        # Textbox for input file
        self.input_file_label = wx.StaticText(self, wx.ID_ANY, _('File: '))
        self.input_file_text_ctrl = wx.TextCtrl(self, wx.ID_ANY, '')
        self.input_file_button = wx.Button(self, wx.ID_ANY, _('Go'))
        self.input_file_button.Bind(wx.EVT_BUTTON,
                                    self.on_input_file_button_click)

        # Sizer for input file, which is hidden by default.
        self.input_file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.input_file_sizer.Add(self.input_file_label)
        self.input_file_sizer.Add(self.input_file_text_ctrl, proportion=1)
        self.input_file_sizer.Add(self.input_file_button)
        self.show_input_file(False)

        # Sizer to set the width of the above text box to 640.
        self.fixed_sizer = wx.BoxSizer(wx.VERTICAL)
        self.fixed_sizer.Add((640, 5))
        self.fixed_sizer.Add(self.input_file_sizer, flag=wx.EXPAND)

        # Top sizer
        self.top_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer.Add(self.preview_panel)
        self.top_sizer.Add(self.fixed_sizer)
        self.SetSizer(self.top_sizer)

        self.label_amarec16x10_warning.Hide();
        self._amarec16x10_warning = None

if __name__ == "__main__":
    import sys
    import wx

    application = wx.App()
    frame = wx.Frame(None, wx.ID_ANY, 'Preview', size=(640, 360))
    preview = PreviewPanel(frame, size=(640, 360))
    layout = wx.BoxSizer(wx.VERTICAL)
    layout.Add(preview)
    frame.SetSizer(layout)
    frame.Show()
    application.MainLoop()
