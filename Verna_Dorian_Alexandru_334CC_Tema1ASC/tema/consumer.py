"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs["name"]

    def treat_operation(self, operation):
        """
        Function in which I treat an operation (either add or remove)
        """
        id = self.id
        market = self.marketplace
        wait_time = self.retry_wait_time

        # result of the operation
        res = False
        # if we have an add operation
        if operation["type"] == "add":
            while not res:
                res = market.add_to_cart(id, operation["product"])
                if not res:
                    time.sleep(wait_time)
        # if we have a remove operaion
        elif operation["type"] == "remove":
            while not res:
                res = market.remove_from_cart(id, operation["product"])
                if not res:
                    time.sleep(wait_time)

    def run(self):
        for operation in self.carts:
            self.id = self.marketplace.new_cart()
            for elem in operation:
                # the quantity of that product to
                # place in the cart
                quantity = elem["quantity"]
                for i in range(0, quantity):
                    self.treat_operation(elem)
            # print the final result
            res_place_order = self.marketplace.place_order(self.id)
            for order in res_place_order:
                print(self.name, "bought", order[1], flush=True)
