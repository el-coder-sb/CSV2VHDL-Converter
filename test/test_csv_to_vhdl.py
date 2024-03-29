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
sys.path.insert(0, os.path.abspath("../"))
import csv_to_vhdl

INPUT_DICT1 = {'filepath': "test_csv_to_vhdl_input_RTB2004_CHAN1.CSV", 'vhdl_signal_name': 'spi_clk_stimu01_sl_s', 'signal': 'CLK', 'RUN_NUM': 1, 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8, 'MIN_FREQ_MHZ': 20, 'ignore_time_ns': 0}
INPUT_DICT2 = {'filepath': "test_csv_to_vhdl_input_RTB2004_CHAN3.CSV", 'vhdl_signal_name': 'spi_mosi_stimu01_sl_s', 'signal': 'CLK', 'RUN_NUM': 2, 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8, 'MIN_FREQ_MHZ': 20, 'ignore_time_ns': 0}
INPUT_DICT_LIST = [INPUT_DICT1, INPUT_DICT2]

PARAM_DICT = {
    'maxDataRows': None,
    'RESOLUTION': "ns",  # legal values: "ns", "ps"
    'VHD_DO_FILENAME': "my_decoded_file.vhd",  # legal extensions: ".do", ".vhd" -> vhdl is recommended due to much shorter simulation time
    'MAX_WAIT_TIME_NS': 10000,  # just to shorten simulation time
    'MAX_SIM_TIME_US': 1000,  # if only up to this time limit simulation is wanted, counts time with MAX_WAIT_TIMES_NS and not real IDLE-times
    'MAX_FREQ_MHZ': 200,
    'DO_SYNC': False,
    'CSV_Delimiter': ','
}


class Test_CSV_TO_VHDL(unittest.TestCase):

    def test_readCsv(self):
        print(f"\n +++ {sys._getframe().f_code.co_name}() +++")

        # # simple w/o max_row
        print(f"\n\tsimple w/o max_row")

        # readCsv() is a generator function!
        read_csv_row_generator = csv_to_vhdl.readCsv("test_csv_to_vhdl_input_RTB2004_CHAN1.CSV", delimiter_arg=',')

        header = next(read_csv_row_generator)
        time_offset = next(read_csv_row_generator)

        matrix = []
        for row in read_csv_row_generator:
            matrix.append(row)

        self.assertEqual(header, ['in s', 'C1 in V'])
        self.assertEqual(time_offset, -2e-07)
        self.assertEqual(matrix[:54], [[-2e-07, 3.36426], [-1.992e-07, 3.33496], [-1.984e-07, 3.40332], [-1.976e-07, 3.40332], [-1.968e-07, 3.38379], [-1.96e-07, 3.36426],
                                  [-1.952e-07, 3.37402], [-1.944e-07, 3.37402], [-1.936e-07, 3.36426], [-1.928e-07, 3.36426], [-1.92e-07, 3.40332], [-1.912e-07, 3.39355],
                                  [-1.904e-07, 3.37402], [-1.896e-07, 3.36426], [-1.888e-07, 3.39355], [-1.88e-07, 3.35449], [-1.872e-07, 3.36426], [-1.864e-07, 3.37402],
                                  [-1.856e-07, 3.37402], [-1.848e-07, 3.39355], [-1.84e-07, 3.37402], [-1.832e-07, 3.39355], [-1.824e-07, 3.39355], [-1.816e-07, 3.40332],
                                  [-1.808e-07, 3.36426], [-1.8e-07, 3.36426], [-1.792e-07, 3.39355], [-1.784e-07, 3.36426], [-1.776e-07, 3.37402], [-1.768e-07, 3.37402],
                                  [-1.76e-07, 3.37402], [-1.752e-07, 3.38379], [-1.744e-07, 3.36426], [-1.736e-07, 3.38379], [-1.728e-07, 3.41309], [-1.72e-07, 3.38379],
                                  [-1.712e-07, 3.36426], [-1.704e-07, 3.42285], [-1.696e-07, 3.41309], [-1.688e-07, 3.39355], [-1.68e-07, 3.37402], [-1.672e-07, 3.36426],
                                  [-1.664e-07, 3.40332], [-1.656e-07, 3.36426], [-1.648e-07, 3.36426], [-1.64e-07, 3.38379], [-1.632e-07, 3.36426], [-1.624e-07, 3.40332],
                                  [-1.616e-07, 3.39355], [-1.608e-07, 3.34473], [-1.6e-07, 3.37402], [-1.592e-07, 3.40332], [-1.584e-07, 3.37402], [-1.576e-07, 3.41309]])

        # # simple with max_row
        print(f"\n\tsimple with max_row")
        # readCsv() is a generator function!
        read_csv_row_generator = csv_to_vhdl.readCsv("test_csv_to_vhdl_input_RTB2004_CHAN1.CSV", delimiter_arg=',', max_row=3)

        header = next(read_csv_row_generator)
        time_offset = next(read_csv_row_generator)

        matrix = []
        for row in read_csv_row_generator:
            matrix.append(row)

        self.assertEqual(header, ['in s', 'C1 in V'])
        self.assertEqual(time_offset, -2e-07)
        self.assertEqual(matrix, [[-2e-07, 3.36426], [-1.992e-07, 3.33496], [-1.984e-07, 3.40332], [-1.976e-07, 3.40332]])

    def test_get_edges(self):
        print(f"\n +++ {sys._getframe().f_code.co_name}() +++")
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

        # # simple w/o ignores time

        # read ro1 outside of for loop as this inits some variables
        logic_family = 3.3  # V
        last_level = 0  if input_matrix[0][1] < 0.5 * logic_family else 1
        level_matrix = [[0.0, last_level]]

        for input in input_matrix:
           detected_edge = csv_to_vhdl.get_edges(input_matrix[0][0], input, last_level, logic_family=3.3, positive_going_voltage=2.0, negative_going_voltage=0.8, ignore_time_ns=0)

           if detected_edge is not None:
            last_level = detected_edge[1]
            level_matrix.append(detected_edge)

        self.assertEqual(level_matrix, [[0.0, 1], [3.9999999996293e-09, 0], [6.3999999995803525e-09, 1]])

        # # simple with ignores time

        last_level = 0  if input_matrix[0][1] < 0.5 * logic_family else 1
        level_matrix = [[0.0, last_level]]

        for input in input_matrix:
           detected_edge = csv_to_vhdl.get_edges(input_matrix[0][0], input, last_level, logic_family=3.3, positive_going_voltage=2.0, negative_going_voltage=0.8, ignore_time_ns=2)

           if detected_edge is not None:
            last_level = detected_edge[1]
            level_matrix.append(detected_edge)
        self.assertEqual(level_matrix, [[0.0, 1], [1.9999999996293e-09, 0], [4.399999999580353e-09, 1]])

    def test_get_and_prepare_csv_data(self):
        print(f"\n +++ {sys._getframe().f_code.co_name}() +++")
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

    def test_write_stimuli_file_simple(self):
        print(f"\n +++ {sys._getframe().f_code.co_name}() +++")
        import difflib
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

        run_num_list = [dict_elem['RUN_NUM'] for dict_elem in INPUT_DICT_LIST]
        signals_list = [dict_elem['signal'] for dict_elem in INPUT_DICT_LIST]
        vhdl_signal_names = [dict_elem['vhdl_signal_name'] for dict_elem in INPUT_DICT_LIST]
        min_freq_list = [dict_elem['MIN_FREQ_MHZ'] for dict_elem in INPUT_DICT_LIST]
        csv_to_vhdl.write_stimuli_file("", all_ch_level_matrix, vhdl_signal_names, run_num_list, signals_list, min_freq_list, PARAM_DICT)

        with open("test_write_stimuli_file_gm.vhd") as f1:
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

    def test_write_stimuli_file_sync(self):
        print(f"\n +++ {sys._getframe().f_code.co_name}() +++")
        import difflib
        print(f"\n\n+++++++++++++++++++++++++++++++++ test_write_stimuli_file_sync\n+++++++++++++++++++++++++++++++++")
        param_dict_local = {
            'maxDataRows': None,
            'RESOLUTION': "ns",  # legal values: "ns", "ps"
            'VHD_DO_FILENAME': "my_decoded_file.vhd",  # legal extensions: ".do", ".vhd" -> vhdl is recommended due to much shorter simulation time
            'MAX_WAIT_TIME_NS': 10000,  # just to shorten simulation time
            'MAX_SIM_TIME_US': 1000,  # if only up to this time limit simulation is wanted, counts time with MAX_WAIT_TIMES_NS and not real IDLE-times
            'MAX_FREQ_MHZ': 200,
            'DO_SYNC': True,
            'CSV_Delimiter': ','
        }
        input_dict1_local = {'vhdl_signal_name': 'spi_clk_stimu01_sl_s', 'signal': 'CLK', 'RUN_NUM': 1, 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8, 'MIN_FREQ_MHZ': 20, 'ignore_time_ns': 0}
        input_dict2_local = {'vhdl_signal_name': 'spi_mosi_stimu01_sl_s', 'signal': 'MOSI', 'RUN_NUM': 1, 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8, 'MIN_FREQ_MHZ': 20, 'ignore_time_ns': 0}
        input_dict3_local = {'vhdl_signal_name': 'spi_clk_stimu02_sl_s', 'signal': 'CLK', 'RUN_NUM': 2, 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8, 'MIN_FREQ_MHZ': 20, 'ignore_time_ns': 0}
        input_dict4_local = {'vhdl_signal_name': 'spi_mosi_stimu02_sl_s', 'signal': 'MOSI', 'RUN_NUM': 2, 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8, 'MIN_FREQ_MHZ': 20, 'ignore_time_ns': 0}
        input_dict_list_local = [input_dict1_local, input_dict2_local, input_dict3_local, input_dict4_local]

        all_ch_level_matrix = [[[0.0, 1],  # CLK 1
                                [9e-06, 0],
                                [10e-06, 1],
                                [14e-06, 0],
                                [22.1e-06, 1]],
                               [[0.0, 1],  # MOSI 1
                                [9e-06, 0],
                                [10.001e-06, 1],
                                [14e-06, 0],
                                [22.11e-06, 1]],
                               [[0.0, 1],  # CLK 2
                                [9e-06, 0],
                                [10.60e-06, 1],
                                [14e-06, 0],
                                [22e-06, 1]],
                               [[0.0, 1],  # MOSI 2
                                [9e-06, 0],
                                [10.61e-06, 1],
                                [14e-06, 0],
                                [22e-06, 1]]]
        run_num_list = [dict_elem['RUN_NUM'] for dict_elem in input_dict_list_local]
        signals_list = [dict_elem['signal'] for dict_elem in input_dict_list_local]
        vhdl_signal_names = [dict_elem['vhdl_signal_name'] for dict_elem in input_dict_list_local]
        min_freq_list = [dict_elem['MIN_FREQ_MHZ'] for dict_elem in input_dict_list_local]
        csv_to_vhdl.write_stimuli_file("", all_ch_level_matrix, vhdl_signal_names, run_num_list, signals_list, min_freq_list, param_dict_local)

        with open("test_write_stimuli_file_sync_gm.vhd") as f1:
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

    def test_csv_to_vhdl_all(self):
        print(f"\n +++ {sys._getframe().f_code.co_name}() +++")
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
#     test_suite = Test_CSV_TO_VHDL()
#     test_suite.test_readCsv()
#     test_suite.test_get_edges()
#     test_suite.test_write_stimuli_file_simple()
#     test_suite.test_write_stimuli_file_sync()
#     test_suite.test_csv_to_vhdl_all()
#     test_suite.test_readCsv()

