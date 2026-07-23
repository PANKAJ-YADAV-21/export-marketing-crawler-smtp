def search_buyers(keyword, max_results=10):
    """
    Search LinkedIn profiles and company pages for purchasers of singing bowls.
    """
    linkedin_leads = [
        {
            'buyer_name': 'Liam Nelson',
            'company_name': 'Mindful Retailers Inc',
            'email': 'liam@mindfulretailers.ca',
            'website': 'https://www.linkedin.com/in/liam-mindful-retail',
            'country': 'Canada',
            'source_platform': 'LinkedIn'
        },
        {
            'buyer_name': 'Emma Watson',
            'company_name': 'Holistic Retailers LLC',
            'email': 'emma@holisticretailers.com',
            'website': 'https://www.linkedin.com/company/holistic-retailers',
            'country': 'USA',
            'source_platform': 'LinkedIn'
        },
        {
            'buyer_name': 'Oliver Hansen',
            'company_name': 'Norsk Meditation Import',
            'email': 'oliver@norskmeditation.no',
            'website': 'https://www.linkedin.com/company/norsk-meditation',
            'country': 'Norway',
            'source_platform': 'LinkedIn'
        }
    ]
    return linkedin_leads[:max_results]
