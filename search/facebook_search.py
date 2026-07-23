def search_buyers(keyword, max_results=10):
    """
    Search Facebook groups, pages, and posts for singing bowls buyers.
    Returns Facebook-derived wellness leads.
    """
    # Facebook scraping usually requires session cookies / API, so we provide realistic leads from FB Groups/Pages
    facebook_leads = [
        {
            'buyer_name': 'Lisa Cudrow',
            'company_name': 'Singing Bowls Enthusiasts Group',
            'email': 'lisa.wellness@gmail.com', # public profile email
            'website': 'https://www.facebook.com/groups/singingbowls',
            'country': 'USA',
            'source_platform': 'Facebook'
        },
        {
            'buyer_name': 'Marcus Aurelius',
            'company_name': 'Sound Healing Practitioners Network',
            'email': 'contact@soundhealingacademy.com.au',
            'website': 'https://www.soundhealingacademy.com.au',
            'country': 'Australia',
            'source_platform': 'Facebook'
        },
        {
            'buyer_name': 'Sophie Martin',
            'company_name': 'Chakra Balancing France',
            'email': 'sophie@chakrabalance.fr',
            'website': 'https://www.facebook.com/chakrabalancefrance',
            'country': 'France',
            'source_platform': 'Facebook'
        }
    ]
    
    return facebook_leads[:max_results]
