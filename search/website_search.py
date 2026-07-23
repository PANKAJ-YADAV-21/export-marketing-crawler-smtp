def search_buyers(keyword, max_results=10):
    """
    Simulates searching and scraping company website contact pages.
    """
    website_leads = [
        {
            'buyer_name': 'Priya Sharma',
            'company_name': 'Veda Sound Healing Center',
            'email': 'priya@vedasound.in',
            'website': 'https://www.vedasound.in',
            'country': 'India',
            'source_platform': 'Website'
        },
        {
            'buyer_name': 'Pierre Dupont',
            'company_name': 'Bol Chantant Imports',
            'email': 'pierre@bolchantantfrance.fr',
            'website': 'https://www.bolchantantfrance.fr',
            'country': 'France',
            'source_platform': 'Website'
        },
        {
            'buyer_name': 'Charlotte Web',
            'company_name': 'Aura Wellness Boutique',
            'email': 'charlotte@aurawellness.com',
            'website': 'https://www.aurawellness.com',
            'country': 'USA',
            'source_platform': 'Website'
        }
    ]
    return website_leads[:max_results]
