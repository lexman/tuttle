# -*- coding: utf8 -*-


class InvalidResourceCollector():
    """ This class class collects the resources to invalidate and their reason, in order to display them to the user
    and remove them all at once
    """
    def __init__(self):
        self._res_and_reason = []
        self._res_urls = set()

    def collect(self, l):
        for resource, reason in l:
            if resource.url not in self._res_urls:
                self._res_and_reason.append((resource, reason))
                self._res_urls.add(resource.url)

    def collect_with_reason(self, list_of_resources, reason):
        for resource in list_of_resources:
            if resource.url not in self._res_urls:
                self._res_and_reason.append((resource, reason))
                self._res_urls.add(resource.url)

    def display(self):
        if self._res_and_reason:
            print "The following resources are not valid any more and will be removed :"
            for resource, reason in self._res_and_reason:
                print "* {} - {}".format(resource.url, reason)

    def remove_resources(self):
        for resource, reason in self._res_and_reason:
            if resource.exists():
                resource.remove()
