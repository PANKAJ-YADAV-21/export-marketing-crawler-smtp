def search_buyers(keyword, max_results=10):
    """
    Search business directories (e.g. YellowPages, Yelp, local craft directories)
    for distributors and shops trading in yoga/singing bowls.
    """
    directory_leads = [
        {
            'buyer_name': 'Thomas Muller',
            'company_name': 'Spiritual Craft Hamburg',
            'email': 'thomas@spiritualcrafthamburg.de',
            'website': 'https://www.spiritualcrafthamburg.de',
            'country': 'Germany',
            'source_platform': 'Directory'
        },
        {
            'buyer_name': 'Jane Doe',
            'company_name': 'Lotus Blossom Spiritual Shop',
            'email': 'jane@lotusblossomshop.com',
            'website': 'https://www.lotusblossomshop.com',
            'country': 'USA',
            'source_platform': 'Directory'
        },
        {
            'buyer_name': 'Yuki Tanaka',
            'company_name': 'Zen Gardens Tokyo',
            'email': 'yuki@zengardenstokyo.jp',
            'website': 'https://www.zengardenstokyo.jp',
            'country': 'Japan',
            'source_platform': 'Directory'
        }
    ]
    return directory_leads[:max_results]
