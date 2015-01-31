#!/usr/bin/env python
# -*- coding: utf8 -*-


class WorkflowError(Exception): 
    """An error in the workflow structure"""
    def __init__(self, message):
        super(WorkflowError, self).__init__(message)    

class FileRessource:
    scheme = 'file'
    
    def __init__(self, url):
        self._url = url
        self._creator_process = None

    def set_creator_process(self, process):
        self._creator_process = process
    
class ShellProcessor:
    name = 'shell'
    
    def __init__(self):
        pass

class Process:
    """ Class wrapping a process. A process has some input resources, some output resources, 
    some code that produces outputs from inputs, a processor that handle the language specificities
    """    
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
    """A helper class to build Process classes from the name of processors and ressources"""
    
    def __init__(self):
        self._ressources_definition = {}
        self._ressources_definition['file'] = FileRessource
        self._processors = {}
        self._processors['shell'] = ShellProcessor
        self._processors['default'] = ShellProcessor

    def extract_scheme(self, url):
        """Extract the scheme from an url"""
        separator_pos = url.find('://')        
        if separator_pos == -1:
            return False
        url_scheme = url[:separator_pos]
        return url_scheme
        
    def build_ressource(self, url):
        scheme = self.extract_scheme(url)
        if scheme == False or scheme not in self._ressources_definition:
            return None
        ResDefClass = self._ressources_definition[scheme]
        return ResDefClass(url)
    
    def build_process(self, processor = None):
        if processor is None:
            return Process(self._processors["default"])
        elif processor in self._processors:
            return Process(self._processors[processor])
        else:
            return False
    
    def process_from_section(self, section, ressources):
        process = self.build_process(section['processor'])
        process.set_code(section['process_code'])
        for input in section['inputs']:
            in_res = None
            if input not in ressources:            
                in_res = self.build_ressource(input)
                ressources[input] = in_res
            else:
                in_res = ressources[input]
            process.add_input(in_res)
        for output in section['outputs']:
            out_res = None
            if output not in ressources:            
                out_res = self.build_ressource(output)
                ressources[output] = in_res
            else:
                out_res = ressources[input]
            if out_res._creator_process != None:
                raise WorkflowError("{} has been already defined in the workflow (processor : {})".format(output, processor.name))            
            out_res.set_creator_process(process)
            process.add_output(out_res)
        return process
        
    def workflow_from_project(self, sections):
        workflow = []
        ressources = {}
        for section in sections:
            process = self.process_from_section(section, ressources)
            workflow.append(process)
        return workflow