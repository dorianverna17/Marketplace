"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""


from cgitb import reset
from threading import Lock

# for unittests
import unittest
import copy

# for logging
import logging
from logging.handlers import RotatingFileHandler
import time

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        self.queues = {}
        self.carts = {}
        self.products = []
        self.no_producers = 0
        self.no_carts = 0

        self.lock_queue_size = Lock()

        # locks for the number of producers and of carts
        self.lock_carts_size = Lock()
        self.lock_producers_size = Lock()

        self.lock_cart_elem = Lock()

        logging.basicConfig(filename='marketplace.log', level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        handler = RotatingFileHandler('marketplace.log', \
            maxBytes=1000000, backupCount=10)
        formatter = logging.Formatter()
        formatter.converter = time.gmtime
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        # put the entry in the log file
        self.logger.info("Enter: register_producer()")

        # increment the number of producers
        self.lock_producers_size.acquire()
        self.no_producers += 1
        self.lock_producers_size.release()

        # compose the name of the producer
        res = "prod" + str(self.no_producers)

        # set the queue size to 0 for that producer
        self.queues[res] = 0
        return res

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        # put the entry in the log file
        self.logger.info("Enter: publish(" + producer_id + ", " + str(product) + ")")

        # if the producer does not exist then return False
        if producer_id not in self.queues:
            return False

        # if the producer queue is full, then wait until
        # it is no more
        if self.queues[producer_id] >= self.queue_size_per_producer:
            return False

        # put the product in the queue
        # the third parameter is the cart that has taken the product
        self.lock_queue_size.acquire()
        self.products.append([producer_id, product, -1])
        self.queues[producer_id] += 1
        self.lock_queue_size.release()

        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """

        # put the entry in the log file
        self.logger.info("new_cart()")

        # increment the number of carts
        self.lock_carts_size.acquire()
        self.no_carts += 1
        self.lock_carts_size.release()
        # initialize the list of products of the cart
        self.carts[self.no_carts] = []
        # return the id of the cart
        return self.no_carts

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        # put the entry in the log file
        self.logger.info("add_to_cart(" + str(cart_id) + ", " + str(product) + ")")

        # see if the cart is registered
        if cart_id not in self.carts:
            return False
        # look for the product and add it
        for elem in self.products:
            if elem[1] == product and elem[2] == -1:
                self.lock_cart_elem.acquire()
                self.carts[cart_id].append(elem)
                elem[2] = cart_id

                self.lock_queue_size.acquire()
                self.queues[elem[0]] -= 1
                self.lock_queue_size.release()

                self.lock_cart_elem.release()
                return True
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """

        # put the entry in the log file
        self.logger.info("remove_from_cart(" + str(cart_id) + \
            ", " + str(product) + ")")

        # see if the cart is registered
        if cart_id not in self.carts:
            return False

        # look for the product and remove it
        for elem in self.carts[cart_id]:
            if elem[1] == product:
                self.lock_cart_elem.acquire()

                self.lock_queue_size.acquire()
                self.queues[elem[0]] += 1
                elem[2] = -1
                self.lock_queue_size.release()

                self.carts[cart_id].remove(elem)

                self.lock_cart_elem.release()
                return True
        return False

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        # put the entry in the log file
        self.logger.info("place_order(" + str(cart_id) + ")")

        # if the cart is not in the list of carts
        # then return False
        if cart_id not in self.carts:
            return False

        # delete these products from the producers queues
        for prod in self.products:
            if prod[2] == cart_id:
                self.lock_queue_size.acquire()
                self.queues[prod[0]] -= 1
                self.products.remove(prod)
                self.lock_queue_size.release()

        # return the list of objects in the cart
        resulted_list = copy.deepcopy(self.carts[cart_id])
        del self.carts[cart_id]
        return resulted_list

# class for the unittests
class TestMarketplace(unittest.TestCase):
    """
    Class made to implement the unittests
    """
    # inner class for product
    class ProductUnittest:
        """
        Class that simulates a Product
        """
        def __init__(self, name, price):
            self.name = name
            self.price = price

    # setUp method for initializing the marketplace method
    def setUp(self):
        self.marketplace = Marketplace(15)

    # here we test register_producer
    def test_register_producer(self):
        market = self.marketplace

        # register first producer
        res = market.register_producer()
        self.assertEqual(res, "prod1")
        self.assertEqual(market.no_producers, 1)
        self.assertEqual(market.queues["prod1"], 0)

        # register second producer
        res = market.register_producer()
        self.assertEqual(res, "prod2")
        self.assertEqual(market.no_producers, 2)
        self.assertEqual(market.queues["prod1"], 0)
        self.assertEqual(market.queues["prod2"], 0)

        # register third producer
        res = market.register_producer()
        self.assertEqual(res, "prod3")
        self.assertEqual(market.no_producers, 3)
        self.assertEqual(market.queues["prod1"], 0)
        self.assertEqual(market.queues["prod2"], 0)
        self.assertEqual(market.queues["prod3"], 0)

    # here we test publish
    def test_publish(self):
        market = self.marketplace

        # register the first producer
        market.register_producer()

        # first producer publish the first product
        product = self.ProductUnittest("id1", 1)
        res = market.publish("prod1", product)
        self.assertTrue(res)
        self.assertEqual(market.queues["prod1"], 1)
        self.assertEqual(market.products[0][1], product)
        self.assertEqual(market.products[0][0], "prod1")

        # first producer publish the second product
        product = self.ProductUnittest("id2", 2)
        res = market.publish("prod1", product)
        self.assertTrue(res)
        self.assertEqual(market.queues["prod1"], 2)
        self.assertEqual(market.products[1][1], product)
        self.assertEqual(market.products[1][0], "prod1")

        # register the second producer
        market.register_producer()

        # second producer publish the first product
        product = self.ProductUnittest("id3", 3)
        res = market.publish("prod2", product)
        self.assertTrue(res)
        self.assertEqual(market.queues["prod2"], 1)
        self.assertEqual(market.products[2][1], product)
        self.assertEqual(market.products[2][0], "prod2")

    # here we test new_cart
    def test_new_cart(self):
        market = self.marketplace

        # add the first cart
        res = market.new_cart()
        self.assertEqual(res, 1)
        self.assertEqual(market.no_carts, 1)
        self.assertEqual(market.carts[1], [])

        # add the second cart
        res = market.new_cart()
        self.assertEqual(res, 2)
        self.assertEqual(market.no_carts, 2)
        self.assertEqual(market.carts[1], [])
        self.assertEqual(market.carts[2], [])

    # here we test add_to_cart
    def test_add_to_cart(self):
        market = self.marketplace
        # create the products
        product1 = self.ProductUnittest("id1", 1)
        product2 = self.ProductUnittest("id2", 2)
        product3 = self.ProductUnittest("id3", 3)

        # register producers
        market.register_producer()
        market.register_producer()
        # publish the products
        market.publish("prod1", product1)
        market.publish("prod1", product2)
        market.publish("prod2", product3)

        # create the carts
        cart_id1 = market.new_cart()
        cart_id2 = market.new_cart()

        # add product1 to cart 1
        res = market.add_to_cart(cart_id1, product1)
        self.assertTrue(res)
        self.assertEqual(market.carts[cart_id1], [["prod1", product1, cart_id1]])

        # add product3 to cart 1
        res = market.add_to_cart(cart_id1, product3)
        self.assertTrue(res)
        self.assertEqual(market.carts[cart_id1], \
            [["prod1", product1, 1], ["prod2", product3, cart_id1]])

        # add product2 to cart 2
        res = market.add_to_cart(cart_id2, product2)
        self.assertTrue(res)
        self.assertEqual(market.carts[cart_id2], [["prod1", product2, cart_id2]])

        # add product1 to cart 2 -> not possible since it is in cart 1
        res = market.add_to_cart(cart_id2, product1)
        self.assertFalse(res)

    # here we test remove_from_cart
    def test_remove_from_cart(self):
        market = self.marketplace
        # create the products
        product1 = self.ProductUnittest("id1", 1)
        product2 = self.ProductUnittest("id2", 2)
        product3 = self.ProductUnittest("id3", 3)

        # register the producers
        market.register_producer()
        market.register_producer()

        # publish the products
        market.publish("prod1", product1)
        market.publish("prod1", product2)
        market.publish("prod2", product3)

        # add the carts
        cart_id1 = market.new_cart()
        cart_id2 = market.new_cart()

        #  add products to cart
        market.add_to_cart(cart_id1, product1)
        market.add_to_cart(cart_id1, product3)
        market.add_to_cart(cart_id2, product2)

        # remove the first product from cart1
        res = market.remove_from_cart(cart_id1, product1)
        self.assertTrue(res)
        self.assertEqual(market.carts[cart_id1], [["prod2", product3, cart_id1]])

        # remove third product from cart1
        res = market.remove_from_cart(cart_id1, product3)
        self.assertTrue(res)
        self.assertEqual(market.carts[cart_id1], [])

        # remove product 2 from cart1 -> not possible
        # since it is not in the cart
        res = market.remove_from_cart(cart_id1, product2)
        self.assertFalse(res)

        # remove product 2 from cart 2
        res = market.remove_from_cart(cart_id2, product2)
        self.assertTrue(res)
        self.assertEqual(market.carts[cart_id2], [])

    # here we test place_order
    def test_place_order(self):
        market = self.marketplace
        # create the products
        product1 = self.ProductUnittest("id1", 1)
        product2 = self.ProductUnittest("id2", 2)
        product3 = self.ProductUnittest("id3", 3)

        # register the producers
        market.register_producer()
        market.register_producer()

        # publish the products
        market.publish("prod1", product1)
        market.publish("prod1", product2)
        market.publish("prod2", product3)

        # add the carts
        cart_id1 = market.new_cart()
        cart_id2 = market.new_cart()

        # add products to carts
        market.add_to_cart(cart_id1, product1)
        market.add_to_cart(cart_id1, product3)
        market.add_to_cart(cart_id2, product2)

        #  place the order for the first cart
        res = market.place_order(cart_id1)
        self.assertEqual(res[0][0], "prod1")
        self.assertEqual(res[0][2], cart_id1)
        self.assertEqual(res[0][1].name, "id1")
        self.assertEqual(res[0][1].price, 1)

        self.assertEqual(res[1][0], "prod2")
        self.assertEqual(res[1][2], cart_id1)
        self.assertEqual(res[1][1].name, "id3")
        self.assertEqual(res[1][1].price, 3)

        # place the order for the second cart
        res = market.place_order(cart_id2)
        self.assertEqual(res[0][0], "prod1")
        self.assertEqual(res[0][2], cart_id2)
        self.assertEqual(res[0][1].name, "id2")
        self.assertEqual(res[0][1].price, 2)
