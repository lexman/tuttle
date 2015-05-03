# -*- coding: utf8 -*-


class InvalidResourceCollector():
    def __init__(self):
        self.res_and_reason = []

    def collect(self, l):
        self.res_and_reason += l

    def collect_with_reason(self, list_of_resources, reason):
        self.res_and_reason += [(resource, reason) for resource in list_of_resources]

    def display(self):
        if self.res_and_reason:
            print "The following resources are not valid any more and will be removed :"
            for resource, reason in self.res_and_reason:
                print "* {} - {}".format(resource.url, reason)

    def remove_resources(self):
        for resource, reason in self.res_and_reason:
            if resource.exists():
                resource.remove()
