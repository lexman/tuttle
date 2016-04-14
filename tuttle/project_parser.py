# -*- coding: utf-8 -*-
from collections import deque

from error import TuttleError
from workflow_builder import WorkflowBuilder
from workflow import Workflow
from os.path import basename


class ParseError(TuttleError):
    def __init__(self, message, filename, line):
        self._message = message
        self._line = line
        self._filename = filename
    
    def __str__(self):
        return "Parse error in file '{}' on line {} : '{}'".format(self._filename, self._line, self._message)
    

class WorkflowError(ParseError):
    pass


class InvalidResourceError(ParseError):
    pass


class InvalidProcessorError(ParseError):
    pass


class LinesStreamer():
    """Provides lines from one or several files
    This class is a helper that provides lines for the parser. Thanks to tuttle file
    format where sections do not need to be ordered, some files can be added on the fly
     to the streamer
    """

    def __init__(self, init_text = ""):
        self._lines = deque(init_text.splitlines())
        self._num_line = 0
        self._eos = True  # End of stream
        self._filename = "_"
        self._file_queue = deque()
        self._eos = False

    def add_file(self, filename):
        base_filename = basename(filename)
        with open(filename, 'rb') as f:
            file_contents = f.read().decode('utf8')
            file_lines = deque(file_contents.splitlines())
        self._file_queue.append((base_filename, file_lines))

    def next_file(self):
        """ Move to the next file to be parsed.
        The file list must bot be empty
        """
        filename, file_lines = self._file_queue.popleft()
        self._filename = filename
        self._lines = file_lines
        self._num_line = 0

    def files_left(self):
        return len(self._file_queue) > 0

    def lines_left(self):
        return len(self._lines) > 0

    def read_line(self):
        """ Reads a line from a file. A file must have been added before calling read_line()
        :return: tuple : (line : string, line number : int, end of stream : boolean)
        """
        while not self.lines_left() and self.files_left():
            self.next_file()
        if not self.lines_left():
            self._eof = True
            self._line = ""
            return "", self._filename, self._num_line, True
        else:
            self._line = self._lines.popleft()
            self._num_line += 1
            self._eos = False
            return self._line, self._filename, self._num_line, False


class ProjectParser():
    """Parser for tuttlefiles.
        The text describing a Workflow is called Projet
        The text describing a Process (dependencies and code)is called a section"""

    def __init__(self):
        self.wb = WorkflowBuilder()
        self.resources = {}
        self._line = ""
        self._num_line = 0
        self._eof = True
        self._filename = "_"

        self._streamer = LinesStreamer()

    def parse_and_check_file(self, filename):
        self._streamer = LinesStreamer()
        self._streamer.add_file(filename)
        return self.parse_and_check_project()

    def parse_and_check_project(self):
        workflow = self.parse_project()
        unreachable = workflow.circular_references()
        if unreachable:
            error_msg = "The following resources references one another as inputs in a circular way that don't allow " \
                        "to choose which one to run first :\n"
            for process in unreachable:
                error_msg += "* {}\n".format(process.id)
            raise WorkflowError(error_msg, self._filename, self._streamer._num_line)
        return workflow

    def set_project(self, text):
        self._streamer = LinesStreamer(text)
        self._num_line = 0
        self._eof = False

    def read_line(self):
        self._line, self._filename, self._num_line, self._eof =  self._streamer.read_line()
        return (self._line, self._num_line, self._eof )

    def is_blank(self, line):
        """ Check whether the current line in a tuttlefile is blank
        """
        if len(line) > 0 and line[0] == "#":
                return True
        line_stripped = line.strip()
        return len(line_stripped) == 0
        
    def parse_dependencies_and_processor(self):
        arrow_pos = self._line.find('<-')
        if arrow_pos == -1:
            raise ParseError("Definition of dependency expected. Or maybe you just got confused with indentation :)",
                               self._filename, self._num_line)
        mark_pos = self._line.find('!')
        if mark_pos == -1:
            mark_pos = len(self._line)
            processor_name = "default"
        else:
            processor_name = self._line[mark_pos + 2:].strip()
        process = self.wb.build_process(processor_name, self._filename, self._num_line)
        if not process:
            raise InvalidProcessorError("Invalid processor : '{}' ".format(processor_name), self._filename, self._num_line)
        input_urls = self._line[arrow_pos + 2:mark_pos].split(',')
        if len(input_urls) > 1 or input_urls[0].strip() != "":
            for input_url in input_urls:
                in_res = self.wb.get_or_build_resource(input_url.strip(), self.resources)
                if in_res is None:
                    raise InvalidResourceError("Invalid resource url : '{}' in inputs".format(input_url.strip()), self._filename, self._num_line)
                process.add_input(in_res)
        outputs_urls = self._line[:arrow_pos].split(',')
        if len(outputs_urls) > 1 or outputs_urls[0].strip() != "":
            for output_url in outputs_urls:
                out_res = self.wb.get_or_build_resource(output_url.strip(), self.resources)
                if out_res is None:
                    raise InvalidResourceError("Invalid resource url : '{}' in outputs".format(output_url.strip()), self._filename, self._num_line)
                if out_res.creator_process is not None:
                    raise WorkflowError("{} has been already defined in the workflow (by processor : {})".format(output_url,
                                        process._processor.name), self._filename, self._num_line)
                out_res.set_creator_process(process)
                process.add_output(out_res)
        return process

    def is_first_process_line(self):
        """ Is the current line a valid first line of a process ? All blank lines must have been skipped before
            Returns a couple (is_first_line : bool, prefix found : string)
        """
        wsp = "\t "
        i = 0
        while wsp.find(self._line[i]) >= 0:
            # Char i of self._line is a white-space
            i += 1
        if i == 0:
            # Line didn't begin by white-spaces. It's not a valid first process line
            return False, "", ""
        else:
            return True, self._line[:i], self._line[i:] + "\n"

    def parse_process_line(self, prefix):
        """ Parses the line as if it is a line of process, beginning by ::prefix::.
        Returns a couple (is_process_line, line)
        is_process_line : 
            True if it is a process line
            False if not
        line :
            The line of the process, with prefix removed"""
        if self._line.startswith(prefix):
            return True, self._line[len(prefix):] + "\n"
        elif self.is_blank(self._line):
            return True, ""
        else:
            return False, ""
    
    def parse_process_code(self):
        """ Parse process code
        """
        line, num_line, eof = self.read_line()
        # Any number of blank lines
        while self.is_blank(line):
            line, num_line, eof = self.read_line()
            if eof:
                return ""
        # Several lines all beginning by white-spaces define a process
        process_code = ""
        is_process_line, wsp_prefix, process_line = self.is_first_process_line()
        while is_process_line and not self._eof:
            process_code += process_line
            self.read_line()
            if self._eof:
                break
            is_process_line, process_line = self.parse_process_line(wsp_prefix)
        if process_line == "\n":
            # Remove carriage return
            process_code = process_code[:-1]
        return process_code

    def parse_section(self):
        """ Parse a whole section : dependency definition + processor type + process code
        All blank lines must have been skipped before
        """
        # Dependency definition
        process = self.parse_dependencies_and_processor()
        process_code = self.parse_process_code()
        process.set_code(process_code)
        return process

    def is_inclusion(self, line):
        """ Check whether the current line is an include statement
        """
        return line.startswith("include ")

    def parse_inclusion(self):
        """ Returns the meaning part of the inclusion : the file name
        parse_inclusion must only be called if is_inclusion have been verified
        """
        return self._line[len("include "):]

    def add_sub_project(self, filename):
        try:
            self._streamer.add_file(filename)
        except IOError:
            msg = "Can't find file '{}' for inclusion".format(filename)
            raise WorkflowError(msg, self._filename, self._streamer._num_line)

    def is_preprocess(self, line):
        """ Check whether the current line is starting a preprocess section
        """
        return line.startswith("|<<")

    def parse_preprocess_declaration(self):
        mark_pos = self._line.find('!')
        if mark_pos == -1:
            processor_name = "default"
        else:
            processor_name = self._line[mark_pos + 2:].strip()
        process = self.wb.build_process(processor_name, self._filename, self._num_line)
        if not process:
            raise InvalidProcessorError("Invalid processor : '{}' ".format(processor_name), self._filename, self._num_line)
        return process

    def parse_preprocess(self):
        """ Returns a preprocess according to the incoming section
        parse_preprocess must only be called if is_preprocess have been verified
        """
        process = self.parse_preprocess_declaration()
        process_code = self.parse_process_code()
        process.set_code(process_code)
        return process

    def parse_project(self):
        """ Parse a full project describing a workflow
        """
        workflow = Workflow(self.resources)
        line, num_line, eof = self.read_line()
        while True:
            while self.is_blank(line):
                line, num_line, eof = self.read_line()
                if eof:
                    return workflow
            if self.is_inclusion(self._line):
                filename = self.parse_inclusion()
                self.add_sub_project(filename)
                line, num_line, eof = self.read_line()
            else:
                process = self.parse_section()
                workflow.add_process(process)
            if self._eof:
                return workflow
