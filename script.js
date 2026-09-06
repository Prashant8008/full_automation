const newsData = [
    {
        id: 1,
        title: "DRDO Launches Project SHIELD for Directed-Energy Warfare",
        category: "DRDO",
        date: "Sep 04, 2026",
        readTime: "4 min read",
        excerpt: "The S-band High-Power Microwave Integrated Evaluation System marks a major push into directed-energy technology to assess electromagnetic damage.",
        image: "https://images.unsplash.com/photo-1544253457-36e6b0ed3a24?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        isHero: true
    },
    {
        id: 2,
        title: "Government Approves ToT for DRDO Conventional Missiles",
        category: "Policy",
        date: "Aug 29, 2026",
        readTime: "5 min read",
        excerpt: "Transfer of Technology approved for all conventional missile systems developed by DRDO to Indian defense industry to support Aatmanirbhar Bharat.",
        image: "https://images.unsplash.com/photo-1599839619722-39751411ea63?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
    },
    {
        id: 3,
        title: "Successful Maiden Flight of 'Kusha' LR-SAM",
        category: "DRDO",
        date: "Sep 02, 2026",
        readTime: "3 min read",
        excerpt: "India's indigenous Long-Range Surface-to-Air Missile achieves critical milestone, acting as a domestic equivalent to the S-400 system.",
        image: "https://images.unsplash.com/photo-1616012489240-62283842189d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
    },
    {
        id: 4,
        title: "IAF and DRDO Prep for PGB-500 Flight Trials",
        category: "Aviation",
        date: "Sep 01, 2026",
        readTime: "4 min read",
        excerpt: "Flight trials of the indigenous 500-kg Precision-Guided Bomb expected in late September to October 2026.",
        image: "https://images.unsplash.com/photo-1517976487492-5750f3195933?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
    },
    {
        id: 5,
        title: "Delegation of Financial Powers (DFP-2026) Launched",
        category: "Policy",
        date: "Jun 15, 2026",
        readTime: "6 min read",
        excerpt: "Defence Minister launches new framework to empower DRDO by streamlining financial processes and accelerating R&D.",
        image: "https://images.unsplash.com/photo-1555848962-6e79363ec58f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
    },
    {
        id: 6,
        title: "India-Belgium Sign Defence Pacts for 70mm Rockets",
        category: "Treaty",
        date: "Sep 03, 2026",
        readTime: "3 min read",
        excerpt: "Agreements include co-production of rockets, marine diesel engines, and cooperation in drones and mine countermeasures.",
        image: "https://images.unsplash.com/photo-1526628953301-3e589a6a8b74?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
    }
];

document.addEventListener('DOMContentLoaded', () => {
    // Populate Hero
    const heroNews = newsData.find(news => news.isHero);
    if(heroNews) {
        document.getElementById('hero-title').textContent = heroNews.title;
        document.getElementById('hero-excerpt').textContent = heroNews.excerpt;
    }

    // Populate Grid
    const grid = document.getElementById('news-grid');
    
    function renderCards(filter = 'all') {
        grid.innerHTML = '';
        
        let filteredData = newsData.filter(news => !news.isHero);
        if (filter !== 'all') {
            filteredData = filteredData.filter(news => news.category === filter);
        }

        filteredData.forEach(news => {
            const card = document.createElement('article');
            card.className = 'news-card';
            
            card.innerHTML = `
                <div class="card-image" style="background-image: url('${news.image}')">
                    <span class="card-category">${news.category}</span>
                </div>
                <div class="card-content">
                    <div class="card-meta">
                        <span><i class="fa-regular fa-calendar"></i> ${news.date}</span>
                        <span><i class="fa-regular fa-clock"></i> ${news.readTime}</span>
                    </div>
                    <h3 class="card-title">${news.title}</h3>
                    <p class="card-excerpt">${news.excerpt}</p>
                    <a href="#" class="read-more">Access Data <i class="fa-solid fa-chevron-right"></i></a>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    // Initial render
    renderCards();

    // Filter logic
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            filterBtns.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            renderCards(e.target.dataset.filter);
        });
    });
});
