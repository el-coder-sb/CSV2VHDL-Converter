#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Test module for csv_to_vhdl.py

    This file is part of CSV2VHDL-Converter .

    CSV2VHDL-Converter  is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CSV2VHDL-Converter  is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CSV2VHDL-Converter .  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import unittest
import sys

# adding "test" to the system path
sys.path.append(os.path.abspath("../"))
import csv_to_vhdl

INPUT_DICT1 = {'filepath': "test_csv_to_vhdl_input_RTB2004_CHAN1.CSV", 'signal_name': 'spi_clk_stimu01_sl_s', 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8, 'time_offset_ns': 10608}
INPUT_DICT2 = {'filepath': "test_csv_to_vhdl_input_RTB2004_CHAN3.CSV", 'signal_name': 'spi_mosi_stimu01_sl_s', 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8, 'time_offset_ns': 10608}
INPUT_DICT_LIST = [INPUT_DICT1, INPUT_DICT2]

PARAM_DICT = {
    'maxDataRows': None,
    'RESOLUTION': "ns",  # legal values: "ns", "ps"
    'VHD_DO_FILENAME': "my_decoded_file.vhd",  # legal extensions: ".do", ".vhd" -> vhdl is recommended due to much shorter simulation time
    'MAX_WAIT_TIME_NS': 10000,  # just to shorten simulation time
    'MAX_SIM_TIME_US': 1000,  # if only up to this time limit simulation is wanted, counts time with MAX_WAIT_TIMES_NS and not real IDLE-times
    'CSV_Delimiter': ','
}


class Test_CSV_TO_VHDL(unittest.TestCase):

    def test_readCsv(self):
        # simple
        header, time_offset, matrix = csv_to_vhdl.readCsv("test_csv_to_vhdl_input_RTB2004_CHAN1.CSV", delimiter_arg=',', max_row=3)

        self.assertEqual(header, ['in s', 'C1 in V'])
        self.assertEqual(time_offset, -2e-07)
        self.assertEqual(matrix, [[-2e-07, 3.36426], [-1.992e-07, 3.33496], [-1.984e-07, 3.40332], [-1.976e-07, 3.40332]])

    def test_get_edges(self):
        input_matrix = [[-3.9990000E-03, 3.32520E+00],
                        [-3.9989992E-03, 3.34473E+00],
                        [-3.9989984E-03, 3.35449E+00],
                        [-3.9989976E-03, 2.33496E+00],
                        [-3.9989968E-03, 1.33496E+00],
                        [-3.9989960E-03, 0.33496E+00],
                        [-3.9989952E-03, 0.36426E+00],
                        [-3.9989944E-03, 1.35449E+00],
                        [-3.9989936E-03, 2.33496E+00],
                        [-3.9989928E-03, 3.34473E+00],
                        [-3.9989920E-03, 3.34473E+00],
                        [-3.9989912E-03, 3.36426E+00]]

        level_matrix = csv_to_vhdl.get_edges(time_offset=0, csvMatrix=input_matrix, logic_family=3.3, positive_going_voltage=2.0, negative_going_voltage=0.8)
        self.assertEqual(level_matrix, [[0.0, 1], [-0.003998996, 0], [-0.0039989936, 1]])

    def test_get_and_prepare_csv_data(self):

        all_ch_level_matrix = csv_to_vhdl.get_and_prepare_csv_data(INPUT_DICT_LIST, PARAM_DICT)
        self.assertEqual(all_ch_level_matrix, [[[0.0, 1],
                                                [9.903999999999999e-07, 0],
                                                [1.4303999999999999e-06, 1],
                                                [1.4504e-06, 0],
                                                [2.2904e-06, 1]],
                                               [[0.0, 0],
                                                [2.672e-07, 1],
                                                [2.9119999999999996e-07, 0],
                                                [3.072e-07, 1],
                                                [3.4479999999999996e-07, 0],
                                                [3.8719999999999997e-07, 1],
                                                [4.248e-07, 0],
                                                [4.672e-07, 1],
                                                [4.912000000000001e-07, 0],
                                                [7.072e-07, 1],
                                                [7.312e-07, 0],
                                                [8.272e-07, 1],
                                                [2.2752e-06, 0]]])

    def test_write_do_file(self):
        all_ch_level_matrix = [[[0.0, 1],
                                [9.903999999999999e-07, 0],
                                [1.4303999999999999e-06, 1],
                                [1.4504e-06, 0],
                                [2.2904e-06, 1]],
                               [[0.0, 0],
                                [2.672e-07, 1],
                                [2.9119999999999996e-07, 0],
                                [3.072e-07, 1],
                                [3.4479999999999996e-07, 0],
                                [3.8719999999999997e-07, 1],
                                [4.248e-07, 0],
                                [4.672e-07, 1],
                                [4.912000000000001e-07, 0],
                                [7.072e-07, 1],
                                [7.312e-07, 0],
                                [8.272e-07, 1],
                                [2.2752e-06, 0]]]
        signal_names_list = [dict_elem['signal_name'] for dict_elem in INPUT_DICT_LIST]
        csv_to_vhdl.write_do_file("", all_ch_level_matrix, signal_names_list, PARAM_DICT)


    def test_csv_to_vhdl_all(self):
        this_path = os.path.dirname(os.path.abspath(__file__))
        input_file = "test_tb_gen_input.vhd"
        sys.argv.append(os.path.join(this_path, input_file))

        csv_to_vhdl.run_csv_to_do_main(INPUT_DICT_LIST, PARAM_DICT)

        import difflib
        with open("test_csv_to_vhdl_output_gm.vhd") as f1:
            f1_text = f1.readlines()
        with open(PARAM_DICT['VHD_DO_FILENAME']) as f2:
            f2_text = f2.readlines()
        # Find and print the diff:
        found_diff = False
        for line in difflib.unified_diff(f1_text, f2_text, fromfile='golden_model', tofile='generated_output', lineterm=''):
            print(line)
            found_diff = True
        if found_diff is True:
            self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()

