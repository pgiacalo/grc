#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: AM Transmitter
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import PyQt5
import osmosdr
import time
import sip



class AM_Modulator(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "AM Transmitter", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("AM Transmitter")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "AM_Modulator")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.tx_samp_rate = tx_samp_rate = 1.92e6
        self.tx_freq = tx_freq = 27.185e6
        self.transmit = transmit = 0
        self.samp_rate = samp_rate = 48000
        self.rf_gain = rf_gain = 20
        self.mic_gain = mic_gain = 5
        self.if_gain = if_gain = 20

        ##################################################
        # Blocks
        ##################################################

        self.tabs = Qt.QTabWidget()
        self.tabs_widget_0 = Qt.QWidget()
        self.tabs_layout_0 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_0)
        self.tabs_grid_layout_0 = Qt.QGridLayout()
        self.tabs_layout_0.addLayout(self.tabs_grid_layout_0)
        self.tabs.addTab(self.tabs_widget_0, 'Audio')
        self.tabs_widget_1 = Qt.QWidget()
        self.tabs_layout_1 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_1)
        self.tabs_grid_layout_1 = Qt.QGridLayout()
        self.tabs_layout_1.addLayout(self.tabs_grid_layout_1)
        self.tabs.addTab(self.tabs_widget_1, 'RF')
        self.top_layout.addWidget(self.tabs)
        _transmit_check_box = Qt.QCheckBox("Transmit")
        self._transmit_choices = {True: 1, False: 0}
        self._transmit_choices_inv = dict((v,k) for k,v in self._transmit_choices.items())
        self._transmit_callback = lambda i: Qt.QMetaObject.invokeMethod(_transmit_check_box, "setChecked", Qt.Q_ARG("bool", self._transmit_choices_inv[i]))
        self._transmit_callback(self.transmit)
        _transmit_check_box.stateChanged.connect(lambda i: self.set_transmit(self._transmit_choices[bool(i)]))
        self.tabs_grid_layout_1.addWidget(_transmit_check_box, 0, 1, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_1.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_1.setColumnStretch(c, 1)
        self._rf_gain_range = qtgui.Range(0, 30, 1, 20, 200)
        self._rf_gain_win = qtgui.RangeWidget(self._rf_gain_range, self.set_rf_gain, "RF Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.tabs_grid_layout_1.addWidget(self._rf_gain_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.tabs_grid_layout_1.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_1.setColumnStretch(c, 1)
        self._mic_gain_range = qtgui.Range(0, 10, 1, 5, 200)
        self._mic_gain_win = qtgui.RangeWidget(self._mic_gain_range, self.set_mic_gain, "Microphone Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.tabs_grid_layout_0.addWidget(self._mic_gain_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self._if_gain_range = qtgui.Range(0, 30, 1, 20, 200)
        self._if_gain_win = qtgui.RangeWidget(self._if_gain_range, self.set_if_gain, "IF Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.tabs_grid_layout_1.addWidget(self._if_gain_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.tabs_grid_layout_1.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_1.setColumnStretch(c, 1)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=(int(tx_samp_rate / samp_rate)),
                decimation=1,
                taps=[],
                fractional_bw=0)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            1024, #size
            samp_rate, #samp_rate
            "", #name
            3, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.01)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Carrier', 'Baseband', 'Modulated', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(3):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.tabs_grid_layout_0.addWidget(self._qtgui_time_sink_x_0_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.qtgui_grbackground_0 = None
        if "default" != 'default':
            bkcolor="background-color: default;"
        else:
            bkcolor=""

        styleSht = self.styleSheet()

        if len('') > 0:
            bkgnd="background-image: url(" + '' + "); background-repeat: repeat_n; background-position: " + "center" + ";"
        else:
            bkgnd = ''

        styleSht += "QWidget{" + bkgnd + bkcolor + "}"

        self.setStyleSheet(styleSht)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_f(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            tx_freq, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.01)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)


        self.qtgui_freq_sink_x_0.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.tabs_grid_layout_1.addWidget(self._qtgui_freq_sink_x_0_win, 3, 1, 1, 1)
        for r in range(3, 4):
            self.tabs_grid_layout_1.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_1.setColumnStretch(c, 1)
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + "hackrf"
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(tx_samp_rate)
        self.osmosdr_sink_0.set_center_freq(tx_freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain((rf_gain * transmit), 0)
        self.osmosdr_sink_0.set_if_gain((if_gain * transmit), 0)
        self.osmosdr_sink_0.set_bb_gain(0, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_float*1, samp_rate,True)
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)
        self.blocks_multiply_const_vxx_1_0 = blocks.multiply_const_ff(transmit)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_cc(transmit)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(mic_gain)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_divide_xx_0 = blocks.divide_ff(1)
        self.blocks_add_const_vxx_0 = blocks.add_const_ff(1)
        self.audio_source_0 = audio.source(samp_rate, '', True)
        self.analog_sig_source_x_1 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, 1000, 1, 0, 0)
        self.analog_const_source_x_1 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 2)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_divide_xx_0, 1))
        self.connect((self.analog_const_source_x_1, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_sig_source_x_1, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.audio_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_divide_xx_0, 0))
        self.connect((self.blocks_divide_xx_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_divide_xx_0, 0), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.blocks_float_to_complex_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_multiply_const_vxx_1_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.qtgui_time_sink_x_0, 2))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_multiply_const_vxx_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "AM_Modulator")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_tx_samp_rate(self):
        return self.tx_samp_rate

    def set_tx_samp_rate(self, tx_samp_rate):
        self.tx_samp_rate = tx_samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.tx_samp_rate)

    def get_tx_freq(self):
        return self.tx_freq

    def set_tx_freq(self, tx_freq):
        self.tx_freq = tx_freq
        self.osmosdr_sink_0.set_center_freq(self.tx_freq, 0)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.tx_freq, self.samp_rate)

    def get_transmit(self):
        return self.transmit

    def set_transmit(self, transmit):
        self.transmit = transmit
        self._transmit_callback(self.transmit)
        self.blocks_multiply_const_vxx_1.set_k(self.transmit)
        self.blocks_multiply_const_vxx_1_0.set_k(self.transmit)
        self.osmosdr_sink_0.set_gain((self.rf_gain * self.transmit), 0)
        self.osmosdr_sink_0.set_if_gain((self.if_gain * self.transmit), 0)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_1.set_sampling_freq(self.samp_rate)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.tx_freq, self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.osmosdr_sink_0.set_gain((self.rf_gain * self.transmit), 0)

    def get_mic_gain(self):
        return self.mic_gain

    def set_mic_gain(self, mic_gain):
        self.mic_gain = mic_gain
        self.blocks_multiply_const_vxx_0.set_k(self.mic_gain)

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.osmosdr_sink_0.set_if_gain((self.if_gain * self.transmit), 0)




def main(top_block_cls=AM_Modulator, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
