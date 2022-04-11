"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time

class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.name = kwargs["name"]

    def run(self):
        # get the id for the producer
        self.id = self.marketplace.register_producer()

        prod = self.products
        market = self.marketplace
        # generate in a loop
        while 1:
            # iterate through the products
            for index in range(0, len(prod)):
                res = False
                quantity = prod[index][1]
                # if we managed to publish that quantity then
                # we go to publish the next product
                while quantity > 0:
                    res = market.publish(self.id, prod[index][0])
                    if res == False:
                        # wait the default waiting time
                        time.sleep(self.republish_wait_time)
                    else:
                        # decrease quantity and wait the
                        # time necessary after publishing
                        # that product
                        quantity -= 1
                        time.sleep(prod[index][2])
