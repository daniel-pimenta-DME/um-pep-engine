#!/usr/bin/env python3
from requests import post

'''
    Class to deal with PDP Policy calls from inside the PEP
'''
class policy_handler:

    def __init__(self, pdp_url: str, pdp_port: int, pdp_policy_endpoint: str):
        self.url = pdp_url
        self.port = pdp_port
        self.endpoint = pdp_policy_endpoint

    '''
        Registers a resource with the specified policy, at the PDP Policy endpoints
        :param policy_body: JSON document containing policy name, description, rules and scopes
        :type policy_body: JSON
        :param jwt: authorization token for the PDP
        :type jwt: string

        Returns: HTTP reply from PDP Policy Endpoint
    '''
    def create_policy(self, policy_body, input_headers):
        headers = input_headers
        data = policy_body
        return post(self.url+':'+self.port+self.endpoint, headers=headers, data=data)