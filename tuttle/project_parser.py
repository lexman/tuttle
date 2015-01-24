#!/usr/bin/env python
# -*- coding: utf-8 -*-
    

class ProjectParser():
    
    def parse_file(self, filename):
        with open(filename) as f:
            self.set_project(f.read())
        return self.parse_project()

    def set_project(self, text):
        self._lines = text.splitlines()
        self._nb_lines = len(self._lines)
        self._num_line = 0
        self._eof = (self._nb_lines == 0)
        
    def read_line(self):
        if not self._eof:
            self._line = self._lines[self._num_line]
            self._num_line = self._num_line + 1
            self._eof = (self._nb_lines == self._num_line)
        else:
            return ""

    def is_blank(self):
        """ Check whether the current line in a tuttlefile is blank
        """
        if len(self._line) > 0 and self._line[0] == "#":
                return True
        line_stripped = self._line.strip()
        return len(line_stripped) == 0
        
    def parse_dependencies_and_processor(self):
        arrow_pos = self._line.find('<-')
        shebang_pos = self._line.find('#!')
        if shebang_pos == -1:
            shebang_pos = len(self._line)
        outputs = self._line[:arrow_pos].split(',')
        inputs = self._line[arrow_pos + 2:shebang_pos].split(',')
        return { 'outputs' : [output.strip() for output in outputs],
                 'inputs' : [input.strip() for input in inputs],
                 'processor' : 'shell',
                 'process_code' : "",
                 
               }
    
    def is_first_process_line(self):
        """ Is the current line a valid first line of a process ? All blank lines must have been skipped before
            Returns a couple (is_first_line : bool, prefix found : string)
        """
        wsp = "\t "
        prefix = ""
        i = 0
        while wsp.find(self._line[i]) >= 0 :
            # Char i of self._line is a white-space
            prefix = prefix + self._line[i]
            i = i + 1
        if i == 0:
            # Line didn't begin by white-spaces. It's not a valid first process line
            return (False, "")
        else :
            return (True, prefix)

    def parse_process_line(self, prefix):
        """ Parses the line as if it is a line of process, beginning by ::prefix::.
        Returns a couple (is_process_line, line)
        is_process_line : 
            True if it is a process line
            False if not
        line :
            The line of the process, with prefix removed"""
        if self._line.startswith(prefix):
            return (True, self._line[len(prefix):])
        else:
            return (False, "")
    
    def parse_section(self):
        """ Parse a whole section : dependancy definition + processor type + process code
        All blank lines must have been skipped before
        """
        self.read_line()
        # Dependancy definition
        section = self.parse_dependencies_and_processor()
        # Any number of blank lines
        while self.is_blank():
            self.read_line()
            if self._eof:
                # Renvoyer mieux que None
                return section
        # Several lines all beginning by white-spaces define a process
        process_code = ""
        (is_process_line, wsp_prefix, ) = self.is_first_process_line()
        while is_process_line:
            (process_line, is_process_line) = self.parse_process_line(line, wsp_prefix)
            self.read_line()
            process_code = process_code + process_line
        section['process_code'] = process_code
        return section

        
    
def parse_project(filename):
    
    with open(filename) as f:
        error_found = False
        num_line = 1
        line = f.readline()
        if line == "":
            # Fin
            pass
        # Any number of blank lines
        while is_blank(line):
            line = f.readline()
            if line == "":
                # Fin
                pass
            num_line = num_line + 1
        # Dependancy definition
        dep_and_proc = parse_dependencies_and_processor(line)
        # Any blank line
        while is_blank(line):
            line = f.readline()
            if line == "":
                # Fin
                pass
            num_line = num_line + 1
        # Several lines all beginning by white-spaces define a process
        process_code = ""
        (wsp_prefix, is_process_line) = is_first_process_line(line)
        while is_process_line:
            (process_line, is_process_line) = parse_process_line(line, wsp_prefix)
            num_line = num_line + 1
            process_code = process_code + process_line
        
# Q : est-ce que le fichier peut se terminer par une définition de dépendances ?
                
def is_blank(line):
    """ Check whether a line in a tuttlefile is blank
    """
    if len(line) > 0 and line[0] == "#":
            return True
    line_stripped = line.strip()
    return len(line_stripped) == 0

