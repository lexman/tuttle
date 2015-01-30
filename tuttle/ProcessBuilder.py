#!/usr/bin/env python
# -*- coding: utf8 -*-


class FileRessource:
    protocol = 'file'
    
    def __init__(self, uri):
        self._uri = uri
    
class ShellProcessor:
    name = 'shell'
    
    def __init__(self):
        pass

class Process:
    
    def __init__(self, processor):
        self._processor = processor
        self._inputs = []
        self._outputs = []
        self._code = None
    
    def add_input(self, input):
        self._inputs.append(input)

    def add_output(self, output):
        self._outputs.append(output)

    def set_code(self, code):
        self._code = code

        
class ProcessBuilder():
    
    def __init__(self):
        self._ressources_definition = {}
        self._ressources_definition['file'] = FileRessource
        self._processors = {}
        self._processors['shell'] = ShellProcessor
        self._processors['default'] = ShellProcessor

    def extract_protocol(self, uri):
        separator_pos = uri.find('://')        
        if separator_pos == -1:
            return False
        uri_protocol = uri[:separator_pos]
        return uri_protocol
        
    def build_ressource(self, uri):
        protocol = self.extract_protocol(uri)
        if protocol == False or protocol not in self._ressources_definition:
            return None
        ResDefClass = self._ressources_definition[protocol]
        return ResDefClass(uri)
    
    def build_process(self, processor = None):
        if processor is None:
            return Process(self._processors["default"])
        elif processor in self._processors:
            return Process(self._processors[processor])
        else:
            return False
    
    def process_from_section(self, section):
        process = self.build_process(section['processor'])
        process.set_code(section['process_code'])
        for input in section['inputs']:
            in_res = self.build_ressource(input)
            process.add_input(in_res)
            self.ressources[input] = inp_res
        for input in section['output']:
            out_res = self.build_ressource(output)
            process.add_output(in_res)
            self.ressources[output] = out_res
        return process
        
