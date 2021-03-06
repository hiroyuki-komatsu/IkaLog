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

import wx
import cv2


class LastResultPanel(wx.Panel):

    def on_game_individual_result(self, context):
        self.latest_frame = cv2.resize(context['engine']['frame'], (640, 360))
        self.Refresh()

    def OnPaint(self, event):
        if self.latest_frame is None:
            return
        width = 640
        height = 360

        frame_rgb = cv2.cvtColor(self.latest_frame, cv2.COLOR_BGR2RGB)

        try:
            self.bmp = wx.Bitmap.FromBuffer(width, height, frame_rgb)
        except:
            self.bmp = wx.BitmapFromBuffer(width, height, frame_rgb)

        dc = wx.BufferedPaintDC(self)
        dc.SetBackground(wx.Brush(wx.RED))
        dc.Clear()
        dc.DrawBitmap(self.bmp, 0, 0)

    def __init__(self, *args, **kwargs):
        self.latest_frame = None
        wx.Panel.__init__(self, *args, **kwargs)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # self.Bind(wx.EVT_SIZE, self.OnResize)
