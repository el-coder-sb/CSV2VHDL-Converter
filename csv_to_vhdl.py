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
import datetime
import os
import math
import time

TEST_MODE = False  # boolean: True, False


def debug_print(str_to_print):
    if TEST_MODE is True:
        print(str_to_print)


def time_wrapper(func):  # accepts all arguments

    def _wrapper(*args, **kwargs):  # accepts all arguments
        start = time.time()
        _return = func(*args, **kwargs)  # execute the actual function

        end = time.time()  # function executed, time is calculated with ms precision

        # calculate execution time is seconds (if t > 0), else in ms
        _exce_time = f"{(end - start):0.2f} s" if int(end - start) > 0 else f"{(end - start)*1e3:0.2f} ms"
        print(f"\t\t\t\t\t\t\t\t\tRuntime '{func.__name__}': {_exce_time}")
        return _return

    return _wrapper


def get_header_info(header_str, device="RTB2004"):
    ''' CURRENTLY NOT USEFULL '''
    if device == "RTB2004":  # Rohde&Schwarz
        pass  # TODO


@time_wrapper
def readCsv(filename, delimiter_arg=',', max_row=None):
    print(f"Read data from {filename} ")
    # matrix = [[] for i in range(numCol)] # for 2D list-array, matrix = [row][col], 0-based-index!
    matrix = []
    matrix_append = matrix.append  # for runtime saving, s. https://towardsdatascience.com/10-techniques-to-speed-up-python-runtime-95e213e925dc

    with open(filename, 'r') as csvfile:
        filereader = csv.reader(csvfile, delimiter=delimiter_arg, quotechar='|')
        header = next(filereader)

        # read first line for offset seperately to fasten foor loop (saving one 'if' sequenz)
        row = next(filereader)
        debug_print(row)
        time_offset = float(row[0])  # depending on null line of osci there might be negative time values which have to be converted via the time_offset
        matrix_append(list(map(float, row)))  # add list with column values converted to float

        # read all further rows     -> put `if max_row is not None` outside of for-loop to fasten loop
        if max_row is not None:
            for row_num, row in enumerate(filereader, start=1):
                # debug_print(row)
                matrix_append(list(map(float, row)))  # add list with column values converted to float
                if row_num >= max_row :
                    break
        else:
            for row_num, row in enumerate(filereader, start=1):
                matrix_append(list(map(float, row)))  # add list with column values converted to float
            # matrix_append([list(map(float, row) for row in filereader)])  # add list with column values converted to float
    # print(f"Time_offset {time_offset}")
    return header, time_offset, matrix  # 0-based-index, matrix[row][col]


@time_wrapper
def get_edges(time_offset, csvMatrix, logic_family=3.3, positive_going_voltage=2.0, negative_going_voltage=0.8, ignore_time_ns=0, max_sim_time_us=100000, max_freq_mhz=2000):
    ''' Find digital level transitions in input data '''
    last_level = 0 if csvMatrix[0][1] < 0.5 * logic_family else 1
    level_matrix = [[0.0, last_level]]
    level_transition_cnt = 0

    for time_logiclevel_tuple in csvMatrix:

        # check voltage level
        voltage_fl = time_logiclevel_tuple[1]
        timestamp = time_logiclevel_tuple[0] + abs(time_offset) - (ignore_time_ns / 1e9)
        if timestamp <= 0:
            continue

        # use hysterese
        if last_level == 0 and (voltage_fl > positive_going_voltage):
                last_level = 1
                level_matrix.append([timestamp, last_level])
                level_transition_cnt += 1
        elif last_level == 1 and (voltage_fl < negative_going_voltage):
                last_level = 0
                level_matrix.append([timestamp, last_level])
                level_transition_cnt += 1

        if level_transition_cnt > (max_sim_time_us * max_freq_mhz):  # break to shorten runtime;
            print(f"in get_edges(): Break because of level_transition_cnt reached {level_transition_cnt} > max_sim_time_us * max_freq_mhz")
            break
    return level_matrix


@time_wrapper
def write_stimuli_file(path, all_ch_level_matrix, vhdl_signal_names, run_num_list, signals_list, min_freq_list, param_dict) -> None:
    TIMESTAMP_IDX = 0
    last_timestamp = 0
    num_timestamps_per_sig_list = [len(all_ch_level_matrix[i]) for i in range(len(all_ch_level_matrix))]  # [5, 12, 210]
    debug_print(f"num_timestamps_per_sig_list {num_timestamps_per_sig_list}")
    filename, file_extension = os.path.splitext(param_dict["VHD_DO_FILENAME"])
    simulation_time_ns = 0

    min_freq_mhz = min(min_freq_list)
    debug_print(f"min_freq_mhz: {min_freq_mhz}")

    do_sync = False
    if param_dict['DO_SYNC'] is True:
        num_different_runs = len(set(run_num_list))  # num of different runs
        debug_print(f"run_num_list: {run_num_list}")
        debug_print(f"num_different_runs: {num_different_runs}")
        if num_different_runs > 1:
            do_sync = True
        else:
            debug_print(f"num_different_runs was < 2 => No sync action possible ")

    with open(os.path.join(path, param_dict["VHD_DO_FILENAME"]), 'w') as dofile:
        if file_extension == '.do':
            str_run_cmd = (os.path.dirname(os.path.realpath(__file__)) + os.sep + param_dict["VHD_DO_FILENAME"]).replace('\\', '/')  # ModelSim needs '/'
            dofile.write(f'#do {str_run_cmd}\n')
            dofile.write('restart -f\n\n')
        elif file_extension == '.vhd':
            dofile.write('\t--\n')
            dofile.write(f'\t-- Measurement data of {param_dict["VHD_DO_FILENAME"]} starts here\n')
            dofile.write('\t--\n')

        nxt_timestamp_per_sig_idx = [0 for i in range(len(vhdl_signal_names))]  # [0, 0, 0]
        nxt_time_neg_offset_per_sig_s_list = [0 for i in range(len(vhdl_signal_names))]

        while nxt_timestamp_per_sig_idx != []:
            nxt_timestamp_list = [all_ch_level_matrix[num][nxt_timestamp_per_sig_idx[num]][TIMESTAMP_IDX] for num in range(len(nxt_timestamp_per_sig_idx))]  # [0.0, 2.76e-07, 1.968e-07]
            debug_print(f"----- nxt_timestamp_list {nxt_timestamp_list}")  # [0.0, 2.76e-07, 1.968e-07]

            for timestamp_idx in range(len(nxt_timestamp_list)):
                nxt_timestamp_list[timestamp_idx] -= nxt_time_neg_offset_per_sig_s_list[timestamp_idx]

            debug_print(f"nxt_timestamp_list {nxt_timestamp_list}")  # [0.0, 2.76e-07, 1.968e-07]
            signal_nxt_timestamp_min_val_idx = min(range(len(nxt_timestamp_list)), key=nxt_timestamp_list.__getitem__)  # signal_nxt_timestamp_min_val_idx = signal with the next min timestamp
            debug_print(f" signal_nxt_timestamp_min_val_idx {signal_nxt_timestamp_min_val_idx}")
            data_tuple = all_ch_level_matrix[signal_nxt_timestamp_min_val_idx][nxt_timestamp_per_sig_idx[signal_nxt_timestamp_min_val_idx]]
            debug_print(f"selected data_tuple: {data_tuple}")
            data_tuple_tmp = data_tuple.copy()
            data_tuple_tmp[TIMESTAMP_IDX] -= nxt_time_neg_offset_per_sig_s_list[signal_nxt_timestamp_min_val_idx]
            debug_print(f"last_timestamp: {last_timestamp}")
            wait_time_tmp_ps = round((data_tuple_tmp[TIMESTAMP_IDX] - last_timestamp) * 1000000000000, 0)
            wait_time_ps = min(wait_time_tmp_ps, (param_dict['MAX_WAIT_TIME_NS'] * 1000))

            # the sync stuff
            if do_sync is True:
                nxt_switching_signal_per_run_list = [None for i in range(num_different_runs)]
                wait_time_s = wait_time_ps / 1E+12
                if (wait_time_s) > (3 * (1 / (min_freq_mhz * 1000000))):  # 3 heuristical value
                    debug_print(f"{wait_time_s} > {3 * (1 / (min_freq_mhz * 1000000))} -> Prüfe auf Sync")
                    # finde für jeden run den nächsten Zeitstempel
                    for run_num in range(num_different_runs):
                        nxt_timestamp_min_this_run_idx = None
                        # gehe alle Signale durch
                        for signal_idx, run_of_signal in enumerate(run_num_list):
                            # prüfe of Signal zu aktuellem run gehört
                            if run_of_signal == (run_num + 1):
                                if nxt_timestamp_min_this_run_idx is None:
                                    nxt_timestamp_min_this_run_idx = signal_idx
                                    nxt_switching_signal_per_run_list[run_num] = signals_list[signal_idx]
                                else:
                                    debug_print(f"signal_idx {signal_idx}")
                                    debug_print(f"nxt_timestamp_min_this_run_idx {nxt_timestamp_min_this_run_idx}")
                                    if nxt_timestamp_list[nxt_timestamp_min_this_run_idx] > nxt_timestamp_list[signal_idx]:
                                        nxt_timestamp_min_this_run_idx = signal_idx
                                        nxt_switching_signal_per_run_list[run_num] = signals_list[signal_idx]
                                debug_print(f"nxt_switching_signal_per_run_list: {nxt_switching_signal_per_run_list}")
                    # check if for every run the next signal is of same type (don´t sync if e.g. next signal is run1=CLK and run2=MOSI)
                    debug_print(f"nxt_switching_signal_per_run_list: {nxt_switching_signal_per_run_list}")
                    if len(set(nxt_switching_signal_per_run_list)) == 1:
                        print("### Mach SYNC")
                        print(f"simulation_time_ns: {simulation_time_ns}")
                        nxt_time_neg_offset_per_sig_s_tmp_list = [0 for i in range(len(vhdl_signal_names))]
                        # ermittle Zeitdifferenz zwischen den Syncsignalen
                        for signal_idx, signal_type in enumerate(signals_list):
                            debug_print(f"signal_idx, signal_type: {signal_idx}, {signal_type}")
                            debug_print(f"signal_nxt_timestamp_min_val_idx {signal_nxt_timestamp_min_val_idx}")
                            if run_num_list[signal_idx] != run_num_list[signal_nxt_timestamp_min_val_idx]:  # do not sync if signal is in same run as signal_nxt_timestamp_min
                                if signal_type == nxt_switching_signal_per_run_list[0]:
                                    debug_print(f"nxt_timestamp_list[signal_idx]: {nxt_timestamp_list[signal_idx]}")
                                    time_delta_ps = round((nxt_timestamp_list[signal_idx] - data_tuple_tmp[TIMESTAMP_IDX]) * 1000000000000)
                                    debug_print(f"time_delta_ps: {time_delta_ps}")
                                    neg_offset_this_run_in_s = time_delta_ps / 1e+12
                                    # speichere Zeitdifferenz als neg. Offset für nächsten Zeitstempel für alle Signale diesen Runs
                                    for signal_idx_loop, run_num_loop in enumerate(run_num_list):
                                        if run_num_loop == run_num_list[signal_idx]:
                                            nxt_time_neg_offset_per_sig_s_tmp_list[signal_idx_loop] = neg_offset_this_run_in_s
                                    print(f"nxt_time_neg_offset_per_sig_s_tmp_list: {nxt_time_neg_offset_per_sig_s_tmp_list}")
                                else:
                                    debug_print(f"signal_type {signal_type} not matching.")
                            else:
                                debug_print("do not sync if signal is in same run as signal_nxt_timestamp_min")

                        # # reduce neg_offset to minimum
                        # get min of nxt_time_neg_offset_per_sig_s_list
                        if max(nxt_time_neg_offset_per_sig_s_tmp_list) == 0.0:
                            print(f"nxt_time_neg_offset_per_sig_s_tmp_list only 0.0 values.")
                        else:
                            min_neg_offset = max(nxt_time_neg_offset_per_sig_s_tmp_list)  # abs min value
                            for signal_idx, neg_offset in enumerate(nxt_time_neg_offset_per_sig_s_list):
                                if neg_offset <= min_neg_offset:
                                    if run_num_list[signal_idx] == run_num_list[signal_nxt_timestamp_min_val_idx]:  # do take min val only if signal is in same run as signal_nxt_timestamp_min
                                        min_neg_offset = neg_offset
                                        run_num_of_min = run_num_list[signal_idx]
                            print(f"min_neg_offset: {min_neg_offset}")
                            print(f"run_num_of_min: {run_num_of_min}")
                            # go again trough the list and add the new neg_offset
                            if max(nxt_time_neg_offset_per_sig_s_tmp_list) >= min_neg_offset:
                                for signal_idx, neg_offset in enumerate(nxt_time_neg_offset_per_sig_s_list):
                                    nxt_time_neg_offset_per_sig_s_list[signal_idx] += nxt_time_neg_offset_per_sig_s_tmp_list[signal_idx] - min_neg_offset
                            else:
                                for signal_idx, neg_offset in enumerate(nxt_time_neg_offset_per_sig_s_list):
                                    if run_num_list[signal_idx] != run_num_list[signal_nxt_timestamp_min_val_idx]:  # do change val if signal is in same run as signal_nxt_timestamp_min
                                        nxt_time_neg_offset_per_sig_s_list[signal_idx] += nxt_time_neg_offset_per_sig_s_tmp_list[signal_idx]
                        print(f"nxt_time_neg_offset_per_sig_s_list: {nxt_time_neg_offset_per_sig_s_list}")

                    else:
                        debug_print(f"set(nxt_switching_signal_per_run_list) {set(nxt_switching_signal_per_run_list)}")
                else:
                    debug_print(f"wait_time_s {wait_time_s} < {3 * (1 / (min_freq_mhz * 1000000))} -> KEIN Sync")

            # cut idle time to 'MAX_WAIT_TIME_NS'
            data_tuple[TIMESTAMP_IDX] -= nxt_time_neg_offset_per_sig_s_list[signal_nxt_timestamp_min_val_idx]
            debug_print(f"data_tuple after sync: {data_tuple}")
            wait_time_tmp_ps = round((data_tuple[TIMESTAMP_IDX] - last_timestamp) * 1000000000000, 0)
            wait_time_ps = min(wait_time_tmp_ps, (param_dict['MAX_WAIT_TIME_NS'] * 1000))
            debug_print(f"wait_time_ps real: {wait_time_tmp_ps}; wait_time_ps used: {wait_time_ps}")
            if wait_time_tmp_ps > wait_time_ps:
                print(f"wait_time_ps was greater than MAX_WAIT_TIME_NS: {wait_time_tmp_ps} ps -> is cutted to {wait_time_ps}ps")

            # writing the file
            if file_extension == '.do':
                if param_dict["RESOLUTION"] == "ns":
                    dofile.write(f"run {round(wait_time_ps/1000,0)}\n")  # convert diff to ns and round to ns
                elif param_dict["RESOLUTION"] == "ps":
                    dofile.write(f"run {wait_time_ps/1000}\n")  # convert diff to ns and round to ps
                else:
                    raise ValueError('RESOLUTION has an illegal value.')
                dofile.write(f"force -freeze {vhdl_signal_names[signal_nxt_timestamp_min_val_idx]} {data_tuple[1]}\n")
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
                dofile.write(f"\t{vhdl_signal_names[signal_nxt_timestamp_min_val_idx]}\t\t<=\t'{data_tuple[1]}';\n")
                simulation_time_ns += round(wait_time_ps / 1000)
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
                del vhdl_signal_names[signal_nxt_timestamp_min_val_idx]
                del run_num_list[signal_nxt_timestamp_min_val_idx]
                del signals_list[signal_nxt_timestamp_min_val_idx]
                del nxt_time_neg_offset_per_sig_s_list[signal_nxt_timestamp_min_val_idx]
            debug_print(f"nxt_timestamp_per_sig_idx {nxt_timestamp_per_sig_idx}")
    print(f"\n{os.path.join(path, param_dict['VHD_DO_FILENAME'])} was written successfully!")


@time_wrapper
def get_and_prepare_csv_data(input_dict_list, param_dict):
    ''' Read csv file(s) and create Matrix/Table from content'''

    from concurrent.futures import ThreadPoolExecutor, as_completed

    all_ch_level_matrix = []
    future_list = []
    csv_filepaths = [dict_elem['filepath'] for dict_elem in input_dict_list]

    with ThreadPoolExecutor(max_workers=2) as executor:
        for file_num, csv_filepath in enumerate(csv_filepaths):
            level_matrix = executor.submit(read_csv_and_get_edges, csv_filepath, file_num, input_dict_list, param_dict)
            future_list.append(level_matrix)
#             all_ch_level_matrix.append(level_matrix)

    for f in future_list:
        all_ch_level_matrix.append(f.result())

    return all_ch_level_matrix


def read_csv_and_get_edges(csv_filepath, file_num, input_dict_list, param_dict):
    header_str, time_offset, csvMatrix = readCsv(csv_filepath, param_dict['CSV_Delimiter'], param_dict["maxDataRows"])
    print(f"Num of rows: {len(csvMatrix)}")
    get_header_info(header_str)  # ZUTUN
    level_matrix = get_edges(time_offset,
                             csvMatrix,
                             input_dict_list[file_num]['logic_family'],
                             input_dict_list[file_num]['POSITIVE_GOING_VOLTAGE'],
                             input_dict_list[file_num]['NEGATIVE_GOING_VOLTAGE'],
                             input_dict_list[file_num]['ignore_time_ns'],
                             param_dict['MAX_SIM_TIME_US'],
                             param_dict['MAX_FREQ_MHZ'])
    debug_print(level_matrix)
    return level_matrix


def run_csv_to_do_main(input_dict_list, param_dict):
    # print params
    [print(key, value) for key, value in param_dict.items()]
    # [dict_elem['filepath'] for dict_elem in input_dict_list], [dict_elem['logic_family'] for dict_elem in input_dict_list]
    all_ch_level_matrix = get_and_prepare_csv_data(input_dict_list, param_dict)
    # all_ch_level_matrix looks like:  [[[0.0, 1], [9.896e-07, 0]], [[2.672e-07, 1],..]] ; all_ch_level_matrix(data_set_file1(timestamp0, logic_level0), ...)
    # print(f" all_ch_level_matrix {all_ch_level_matrix}")
    vhdl_signal_names = [dict_elem['vhdl_signal_name'] for dict_elem in input_dict_list]
    signals_list = [dict_elem['signal'] for dict_elem in input_dict_list]
    run_num_list = [dict_elem['RUN_NUM'] for dict_elem in input_dict_list]
    min_freq_list = [dict_elem['MIN_FREQ_MHZ'] for dict_elem in input_dict_list]
    write_stimuli_file(os.path.dirname(input_dict_list[0]['filepath']), all_ch_level_matrix, vhdl_signal_names, run_num_list, signals_list, min_freq_list, param_dict)


if __name__ == '__main__':

    param_dict = {
        'maxDataRows': None,
        'RESOLUTION': "ns",  # legal values: "ns", "ps"
        'VHD_DO_FILENAME': "my_decoded_file.vhd",  # legal extensions: ".do", ".vhd" -> vhdl is recommended due to much shorter simulation time
        'MAX_WAIT_TIME_NS': 10000,  # just to shorten simulation time
        'MAX_SIM_TIME_US': 2000,  # if just up to this time limit simulation is wanted, counts time with MAX_WAIT_TIMES_NS and not real IDLE-times
        'MAX_FREQ_MHZ': 200,  # currently only used to calc break because of MAX_SIM_TIME_US to shorten runtime,
                                # either the maximum possible frequency of the oscilloscope or the maximum expected signal frequency
        'DO_SYNC': True,
        'CSV_Delimiter': ','
    }

    default_input_dict = {'logic_family': 3.3, 'POSITIVE_GOING_VOLTAGE': 2.0, 'NEGATIVE_GOING_VOLTAGE': 0.8, 'MIN_FREQ_MHZ': 20}

    if TEST_MODE is True:
        input_dict1 = dict({'filepath': r"RTA4004_CH1_CLK_01.CSV", 'vhdl_signal_name': 'spi_clk_stimu01_sl_s', 'signal': 'CLK', 'RUN_NUM': 1, 'ignore_time_ns': 10608}, ** default_input_dict)  # concat dicts
        input_dict2 = dict({'filepath': r"RTA4004_CH4_MOSI_01.CSV", 'vhdl_signal_name': 'spi_mosi_stimu01_sl_s', 'signal': 'MOSI', 'RUN_NUM': 1, 'ignore_time_ns': 10608}, ** default_input_dict)
        input_dict3 = dict({'filepath': r"RTA4004_CH1_CLK_02.CSV", 'vhdl_signal_name': 'spi_clk_stimu02_sl_s', 'signal': 'CLK', 'RUN_NUM': 2, 'ignore_time_ns': 0}, ** default_input_dict)
        input_dict4 = dict({'filepath': r"RTA4004_CH4_MOSI_02.CSV", 'vhdl_signal_name': 'spi_mosi_stimu02_sl_s', 'signal': 'MOSI', 'RUN_NUM': 2, 'ignore_time_ns': 0}, ** default_input_dict)
        input_dict_list = [input_dict1, input_dict2, input_dict3, input_dict4]
    else:
        #  'POSITIVE_GOING_VOLTAGE': in V, "NEGATIVE_GOING_VOLTAGE": in V, 'logic_family' in V
        #  'ignore_time_ns' typischerweise aus ModelSim-Wave ablesen
        #  'IS_CLK', 'RUN_NUM' and 'CLK_FREQ_MHZ' only used for sync
        input_dict1 = dict({'filepath': r"RTA4004_CH1_CLK_01.CSV", 'vhdl_signal_name': 'spi_clk_stimu01_sl_s', 'signal': 'CLK', 'RUN_NUM': 1, 'ignore_time_ns': 10608}, ** default_input_dict)  # concat dicts
        input_dict2 = dict({'filepath': r"RTA4004_CH4_MOSI_01.CSV", 'vhdl_signal_name': 'spi_mosi_stimu01_sl_s', 'signal': 'MOSI', 'RUN_NUM': 1, 'ignore_time_ns': 10608}, ** default_input_dict)
        input_dict3 = dict({'filepath': r"RTA4004_CH1_CLK_02.CSV", 'vhdl_signal_name': 'spi_clk_stimu02_sl_s', 'signal': 'CLK', 'RUN_NUM': 2, 'ignore_time_ns': 0}, ** default_input_dict)
        input_dict4 = dict({'filepath': r"RTA4004_CH4_MOSI_02.CSV", 'vhdl_signal_name': 'spi_mosi_stimu02_sl_s', 'signal': 'MOSI', 'RUN_NUM': 2, 'ignore_time_ns': 0}, ** default_input_dict)
        input_dict_list = [input_dict1, input_dict2, input_dict3, input_dict4]

    starttime = datetime.datetime.now()
    run_csv_to_do_main(input_dict_list, param_dict)
    runtime = datetime.datetime.now() - starttime
    print(f"runtime: {runtime}")
