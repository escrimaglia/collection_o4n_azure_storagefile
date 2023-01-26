# coding: utf-8
# By Ed Scrimaglia

from __future__ import (absolute_import, division, print_function)
import re


"""
FILE: slelect_files_from_pattern.py
DESCRIPTION:
    These python class allows selecting files from a local directory or azure storage share
    according to a pattern provided as input returnig a list of file name.
USAGE:
    from module_utils.select_files_from_pattern import SelectFiles 
    Patterns allowed:
    file*
    file*.txt
    file*.tx*
    file.tx*
    *.txt
    file.*
    *.*
    file.txt
"""

class SelectFiles():
    def select_files(self, _file_pattern, _files_in_dir):
        msg_ret = f"Files selection done for <{_file_pattern}>"
        status = True
        name_and_exension_pattern = re.split(r"\.", _file_pattern)
        pattern_file_ext = name_and_exension_pattern[1] if len(name_and_exension_pattern) == 2 else []
        pattern_file_name = name_and_exension_pattern[0]
        try:
            if _file_pattern == "*.*":  # *.*
                return status, msg_ret, _files_in_dir
            elif len(name_and_exension_pattern) == 1:  # file*
                file_name_pattern = re.split(r"\*", pattern_file_name)[0]
                return status, msg_ret, [file for file in _files_in_dir if re.split(r"\.", file)[0].startswith(file_name_pattern)]
            elif len(name_and_exension_pattern) == 2:
                if pattern_file_name.startswith("*") and not "*" in pattern_file_ext:  # *.txt
                    return status, msg_ret, [file for file in _files_in_dir if pattern_file_ext == re.split(r"\.", file)[1]]
                elif pattern_file_ext.startswith("*") and not "*" in pattern_file_name:  # file.*
                    return status, msg_ret, [file for file in _files_in_dir if pattern_file_name == re.split(r"\.", file)[0]]
                elif "*" in pattern_file_name and not "*" in pattern_file_ext:  # file*.txt
                    name_pattern = re.split(r"\*", pattern_file_name)[0]
                    return status, msg_ret, [file for file in _files_in_dir if
                                             file.startswith(name_pattern) and pattern_file_ext == re.split(r"\.", file)[1]]
                elif not "*" in pattern_file_name and "*" in pattern_file_ext:  # file.t*
                    file_ext_pattern = re.split(r"\*", pattern_file_ext)[0]
                    return status, msg_ret, [file for file in _files_in_dir if pattern_file_name == re.split(r"\.", file)[0]
                                             and file_ext_pattern in re.split(r"\.", file)[1]]
                elif "*" in pattern_file_name and "*" in pattern_file_ext:  # file*.t*
                    file_name_pattern = re.split(r"\*", pattern_file_name)[0]
                    file_ext_pattern = re.split(r"\*", pattern_file_ext)[0]
                    return status, msg_ret, [file for file in _files_in_dir if re.split(r"\.", file)[0].startswith(file_name_pattern)
                                             and re.split(r"\.", file)[1].startswith(file_ext_pattern)]
                elif "*" in pattern_file_name and pattern_file_ext == "*":  # file*.*
                    file_name_pattern = re.split(r"\*", pattern_file_name)[0]
                    file_ext_pattern = pattern_file_ext
                    return status, msg_ret, [file for file in _files_in_dir if
                                             re.split(r"\.", file)[0].startswith(file_name_pattern)
                                             and re.split(r"\.", file)[1] == "*"]
                elif not "*" in pattern_file_name and not "*" in pattern_file_ext:  # file.txt
                    file_name_pattern = pattern_file_name
                    file_ext_pattern = pattern_file_ext
                    return status, msg_ret, [file for file in _files_in_dir if file_name_pattern == re.split(r"\.", file)[0]
                                             and file_ext_pattern == re.split(r"\.", file)[1]]
                else:
                    status = False
                    msg_ret = f"Invalid file name: <{_file_pattern}>"
                    return status, msg_ret, []
            else:
                status = False
                msg_ret = f"Invalid file name: <{_file_pattern}>"
                return status, msg_ret, []
        except Exception as error:
            status = False
            msg_ret = f"Files selection failed for <{_file_pattern}> pattern, error: <{error.args}>"
            return status, msg_ret, []