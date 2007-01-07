from Products.PloneTestCase import five

class PloneSession:

    def setUp(cls):
        '''Sets up the site(s).'''
        five.safe_load_site()
    setUp = classmethod(setUp)

    def tearDown(cls):
        '''Removes the site(s).'''
        five.cleanUp()
    tearDown = classmethod(tearDown)
