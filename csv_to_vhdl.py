#! python3
# -*- coding: utf-8 -*-
'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Dieses Programm ist Freie Software: Sie können es unter den Bedingungen
    der GNU General Public License, wie von der Free Software Foundation,
    Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
    veröffentlichten Version, weiter verteilen und/oder modifizieren.

    Dieses Programm wird in der Hoffnung bereitgestellt, dass es nützlich sein wird, jedoch
    OHNE JEDE GEWÄHR,; sogar ohne die implizite
    Gewähr der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
    Siehe die GNU General Public License für weitere Einzelheiten.

    Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
    Programm erhalten haben. Wenn nicht, siehe <https://www.gnu.org/licenses/>.

Created on 31.08.2020

This python-script reads csv-data (e.g. taken from a oscilloscope measurement) and generates vhdl code, to be used in a simulation.

@author: Simon Buhrow
'''

import csv
import os
import math

TEST_MODE = True  # False


def debug_print(str_to_print):
    if TEST_MODE is True:
        print(str_to_print)


def get_header_info(header_str, device="RTB2004"):
    ''' CURRENTLY NOT USEFULL '''
    if device == "RTB2004":  # Rohde&Schwarz
        pass  # TODO


def readCsv(filename, delimiter_arg=',', max_row=None):
    print(f"Read data from {filename} ")
    # matrix = [[] for i in range(numCol)] # for 2D list-array, matrix = [row][col], 0-based-index!
    matrix = []

    with open(filename, 'r') as csvfile:
        filereader = csv.reader(csvfile, delimiter=delimiter_arg, quotechar='|')
        header = next(filereader)
        for row_num, row in enumerate(filereader):
            debug_print(row)
            if row_num == 0:
                time_offset = float(row[0])
            matrix.append([])
            for col_str in row:
                matrix[row_num].append(float(col_str))
            if max_row is not None and row_num == max_row:
                break
    # print(f"Time_offset {time_offset}")
    return header, time_offset, matrix  # 0-based-index, matrix[row][col]


def get_edges(time_offset, csvMatrix, logic_family=3.3, positive_going_voltage=2.0, negative_going_voltage=0.8):
    ''' Find digital level transitions in input data '''
    last_level = 0 if csvMatrix[0][1] < 0.5 * logic_family else 1
    level_matrix = [[0.0, last_level]]

    for time_logiclevel_tuple in csvMatrix:
        # checke Spannungslevel
        voltage_fl = time_logiclevel_tuple[1]

        # benutze Hysterese
        if last_level == 0 and (voltage_fl > positive_going_voltage):
                last_level = 1
                timestamp = time_logiclevel_tuple[0] + abs(time_offset)
                level_matrix.append([timestamp, last_level])
        elif last_level == 1 and (voltage_fl < negative_going_voltage):
                last_level = 0
                timestamp = time_logiclevel_tuple[0] + abs(time_offset)
                level_matrix.append([timestamp, last_level])

    return level_matrix


def write_stimuli_file(path, all_ch_level_matrix, signal_names_list, param_dict) -> None:
    TIMESTAMP_IDX = 0
    last_timestamp = 0
    num_timestamps_per_sig_list = [len(all_ch_level_matrix[i]) for i in range(len(all_ch_level_matrix))]  # [5, 12, 210]
    debug_print(f"num_timestamps_per_sig_list {num_timestamps_per_sig_list}")
    filename, file_extension = os.path.splitext(param_dict["VHD_DO_FILENAME"])
    simulation_time_ns = 0

    with open(os.path.join(path, param_dict["VHD_DO_FILENAME"]), 'w') as dofile:
        if file_extension == '.do':
            str_run_cmd = (os.path.dirname(os.path.realpath(__file__)) + os.sep + param_dict["VHD_DO_FILENAME"]).replace('\\', '/')  # ModelSim needs '/'
            dofile.write(f'#do {str_run_cmd}\n')
            dofile.write('restart -f\n\n')
        elif file_extension == '.vhd':
            dofile.write('\t--\n')
            dofile.write(f'\t-- Measurement data of {param_dict["VHD_DO_FILENAME"]} starts here\n')
            dofile.write('\t--\n')

        nxt_timestamp_per_sig_idx = [0 for i in range(len(signal_names_list))]  # [0, 0, 0]

        while nxt_timestamp_per_sig_idx != []:
            nxt_timestamp_list = [all_ch_level_matrix[num][nxt_timestamp_per_sig_idx[num]][TIMESTAMP_IDX] for num in range(len(nxt_timestamp_per_sig_idx))]  # [0.0, 2.76e-07, 1.968e-07]
            debug_print(f"nxt_timestamp_list {nxt_timestamp_list}")  # [0.0, 2.76e-07, 1.968e-07]
            signal_nxt_timestamp_min_val_idx = min(range(len(nxt_timestamp_list)), key=nxt_timestamp_list.__getitem__)  # signal_nxt_timestamp_min_val_idx = signal with the next min timestamp
            debug_print(f" signal_nxt_timestamp_min_val_idx {signal_nxt_timestamp_min_val_idx}")
            data_tuple = all_ch_level_matrix[signal_nxt_timestamp_min_val_idx][nxt_timestamp_per_sig_idx[signal_nxt_timestamp_min_val_idx]]

            debug_print(data_tuple)
            debug_print(last_timestamp)
            wait_time_ps = round((data_tuple[TIMESTAMP_IDX] - last_timestamp) * 1000000000000, 0)
            debug_print(f"wait_time_ps real: {wait_time_ps}")
            if wait_time_ps > (param_dict['MAX_WAIT_TIME_NS'] * 1000):
                print(f"wait_time_ps is greater than MAX_WAIT_TIME_NS: {wait_time_ps} ps -> will be cutted to {param_dict['MAX_WAIT_TIME_NS']*1000}ps")
                wait_time_ps = min(wait_time_ps, (param_dict['MAX_WAIT_TIME_NS'] * 1000))
            debug_print(f"wait_time_ps: {wait_time_ps}")
            if file_extension == '.do':
                if param_dict["RESOLUTION"] == "ns":
                    dofile.write(f"run {round(wait_time_ps/1000,0)}\n")  # convert diff to ns and round to ns
                elif param_dict["RESOLUTION"] == "ps":
                    dofile.write(f"run {wait_time_ps/1000}\n")  # convert diff to ns and round to ps
                else:
                    raise ValueError('RESOLUTION has an illegal value.')
                dofile.write(f"force -freeze {signal_names_list[signal_nxt_timestamp_min_val_idx]} {data_tuple[1]}\n")
                # -deposit
                # (optional) Sets the object to the specified <value>. The <value> remains until the object is
                # forced again,
            elif file_extension == '.vhd':
                num_max_digits = int(math.log10(param_dict['MAX_WAIT_TIME_NS'])) + 1  # +1 to round up, ceil does not work for MAX_WAIT_TIME_NS=10,100,1000,...

                if param_dict["RESOLUTION"] == "ns":
                    dofile.write(f"\twait for {round(wait_time_ps / 1000, 0): >{num_max_digits}} ns;\t")  # convert diff to ns and round to ns; +2-> because of ".0" in output format
                elif param_dict["RESOLUTION"] == "ps":
                    dofile.write(f"\twait for {wait_time_ps: >{num_max_digits+3}} ps;\t")  # convert diff to ns and round to ps; +4-> ".000"
                else:
                    raise ValueError('RESOLUTION has an illegal value.')
                dofile.write(f"\t{signal_names_list[signal_nxt_timestamp_min_val_idx]}\t\t<=\t'{data_tuple[1]}';\n")
                simulation_time_ns += int(wait_time_ps / 1000)
                debug_print(f"simulation_time_ns: {simulation_time_ns}")
                if simulation_time_ns > (param_dict['MAX_SIM_TIME_US'] * 1000):
                    print(f"BREAK as MAX_SIM_TIME_US is reached.")
                    break
            last_timestamp = data_tuple[TIMESTAMP_IDX]
            nxt_timestamp_per_sig_idx[signal_nxt_timestamp_min_val_idx] += 1
            # check if signal has no more transitions
            if nxt_timestamp_per_sig_idx[signal_nxt_timestamp_min_val_idx] == num_timestamps_per_sig_list[signal_nxt_timestamp_min_val_idx]:
                del nxt_timestamp_per_sig_idx[signal_nxt_timestamp_min_val_idx]
                del all_ch_level_matrix[signal_nxt_timestamp_min_val_idx]
                del num_timestamps_per_sig_list[signal_nxt_timestamp_min_val_idx]
                del signal_names_list[signal_nxt_timestamp_min_val_idx]
            debug_print(f"nxt_timestamp_per_sig_idx {nxt_timestamp_per_sig_idx}")
    print(f"\n{os.path.join(path, param_dict['VHD_DO_FILENAME'])} was written successfully!")


def get_and_prepare_csv_data(input_dict_list, param_dict):
    ''' Read csv file(s) and create Matrix/Table from content'''
    all_ch_level_matrix = []
    csv_filepaths = [dict_elem['filepath'] for dict_elem in input_dict_list]

    for file_num, csv_filepath in enumerate(csv_filepaths):
        header_str, time_offset, csvMatrix = readCsv(csv_filepath, param_dict['CSV_Delimiter'], param_dict["maxDataRows"])
        print(f"Num of rows: {len(csvMatrix)}")
        get_header_info(header_str)  # ZUTUN
        level_matrix = get_edges(time_offset, csvMatrix, input_dict_list[file_num]['logic_family'], input_dict_list[file_num]['POSITIVE_GOING_VOLTAGE'], input_dict_list[file_num]['NEGATIVE_GOING_VOLTAGE'])
        debug_print(level_matrix)

        all_ch_level_matrix.append(level_matrix)

    return all_ch_level_matrix


def run_csv_to_do_main(input_dict_list, param_dict):
    # print params
    [print(key, value) for key, value in param_dict.items()]
    # [dict_elem['filepath'] for dict_elem in input_dict_list], [dict_elem['logic_family'] for dict_elem in input_dict_list]
    all_ch_level_matrix = get_and_prepare_csv_data(input_dict_list, param_dict)
    # all_ch_level_matrix looks like:  [[[0.0, 1], [9.896e-07, 0]], [[2.672e-07, 1],..]] ; all_ch_level_matrix(data_set_file1(timestamp0, logic_level0), ...)
    # print(f" all_ch_level_matrix {all_ch_level_matrix}")
    signal_names = [dict_elem['signal_name'] for dict_elem in input_dict_list]
    write_stimuli_file(os.path.dirname(input_dict_list[0]['filepath']), all_ch_level_matrix, signal_names, param_dict)


if __name__ == '__main__':

    param_dict = {
        'maxDataRows': None,
        'RESOLUTION': "ns",  # legal values: "ns", "ps"
        'VHD_DO_FILENAME': "my_decoded_file.vhd",  # legal extensions: ".do", ".vhd" -> vhdl is recommended due to much shorter simulation time
        'MAX_WAIT_TIME_NS': 10000,  # just to shorten simulation time
        'MAX_SIM_TIME_US': 4000,  # if just up to this time limit simulation is wanted, counts time with MAX_WAIT_TIMES_NS and not real IDLE-times
        'CSV_Delimiter': ';'
    }

    if TEST_MODE is True:
        #  'POSITIVE_GOING_VOLTAGE': in V, "NEGATIVE_GOING_VOLTAGE": in V, 'logic_family' in V
        input_dict1 = {'filepath': r'C:\CSV_to_DO\erste_schritt\RTB2004_CHAN1.CSV', 'signal_name': 'spi_miso_sl_i_s', 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8}
        # input_dict2 = {'filepath': r'C:\CSV_to_DO\erste_schritt\RTB2004_CHAN3.CSV', 'signal_name': 'spi_mosi_sl_i_s', 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8}
        # input_dict3 = {'filepath': r'C:\CSV_to_DO\erste_schritt\RTB2004_CHAN4.CSV', 'signal_name': 'spi_clk_sl_i_s', 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8}
        # input_dict_list = [input_dict1, input_dict2, input_dict3]
        input_dict_list = [input_dict1]
    else:
        #  'POSITIVE_GOING_VOLTAGE': in V, "NEGATIVE_GOING_VOLTAGE": in V, 'logic_family' in V
        input_dict1 = {'filepath': r"C:\OszilloskopDaten\RTB2004_CH1_MISO_ENDE_02.CSV", 'signal_name': 'spi_miso_sl_i_s', 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8}
        input_dict2 = {'filepath': r"C:\OszilloskopDaten\RTB2004_CH3_MOSI_ENDE_02.CSV", 'signal_name': 'spi_mosi_sl_i_s', 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8}
        input_dict3 = {'filepath': r"C:\OszilloskopDaten\RTB2004_CH4_CLK_ENDE_02.CSV", 'signal_name': 'spi_clk_sl_i_s', 'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8}
        input_dict_list = [input_dict1, input_dict2, input_dict3]
        # input_dict_list = [input_dict3]

    run_csv_to_do_main(input_dict_list, param_dict)
