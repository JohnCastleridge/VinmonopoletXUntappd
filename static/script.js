// Kolonne-konfigurasjon
const COLUMNS = [
    // --- HOVEDKOLONNER (niche: false) ---
    { id: 'image', title: 'Bilde', type: 'none', visible: true, niche: false, width: '100px', render: (row) => {
        let imgSrc = row.vmp_image || row.url_image;
        if (imgSrc === 'https://assets.untappd.com/') imgSrc = null;
        return imgSrc ? `<img src="${imgSrc}" class="beer-img" loading="lazy">` : '';
    }},
    { id: 'links', title: 'Lenker', type: 'none', visible: true, niche: false, width: '120px', render: (row) => {
        let html = `<a href="https://www.vinmonopolet.no/p/${row.product_id_vmp}" target="_blank" onclick="event.stopPropagation()" title="Se på Vinmonopolet" style="text-decoration:none; margin-right:5px; background:var(--bg-dark); padding:4px 6px; border-radius:4px; border:1px solid var(--border); font-size:1.1rem; display:inline-block;">🍇</a>`;
        if (row.url_unt) html += `<a href="${row.url_unt}" target="_blank" onclick="event.stopPropagation()" title="Se på Untappd" style="text-decoration:none; background:var(--bg-dark); padding:4px 6px; border-radius:4px; border:1px solid var(--border); font-size:1.1rem; display:inline-block;">🍺</a>`;
        return html;
    }},
    { id: 'match_confidence', title: 'Match (%)', type: 'number', visible: true, niche: false, width: '100px', render: (row) => row.match_confidence ? `${row.match_confidence.toFixed(1)}%` : '-' },
    
    { id: 'vmp_name', title: 'Navn (VMP)', type: 'text', visible: true, niche: false, width: '250px', render: (row) => row.vmp_name },
    { id: 'unt_name', title: 'Navn (Untappd)', type: 'text', visible: false, niche: false, width: '250px', render: (row) => row.unt_name || '-' },
    
    { id: 'vmp_brewery', title: 'Produsent (VMP)', type: 'text', visible: false, niche: false, width: '200px', render: (row) => row.vmp_brewery || '-' },
    { id: 'unt_brewery', title: 'Bryggeri (Untappd)', type: 'text', visible: true, niche: false, width: '200px', render: (row) => row.unt_brewery || '-' },
    
    { id: 'vmp_country', title: 'Land', type: 'text', visible: false, niche: false, width: '120px', render: (row) => row.vmp_country || '-' },
    { id: 'vmp_main_category', title: 'Hovedkategori', type: 'text', visible: false, niche: false, width: '140px', render: (row) => row.vmp_main_category || '-' },
    { id: 'vmp_style', title: 'Stil (VMP)', type: 'text', visible: false, niche: false, width: '150px', render: (row) => row.vmp_style || '-' },
    { id: 'unt_style', title: 'Understil (Untappd)', type: 'text', visible: false, niche: false, width: '180px', render: (row) => row.unt_style || '-' },
    
    { id: 'price', title: 'Pris', type: 'number', visible: true, niche: false, width: '100px', render: (row) => row.price ? `${row.price.toFixed(2)} kr` : '-' },
    { id: 'volume_ml', title: 'Volum (ml)', type: 'number', visible: false, niche: false, width: '100px', render: (row) => row.volume_ml ? `${row.volume_ml} ml` : '-' },
    { id: 'price_per_liter', title: 'Pris pr. Liter', type: 'number', visible: false, niche: false, width: '120px', render: (row) => row.price_per_liter ? `${row.price_per_liter.toFixed(2)} kr` : '-' },
    
    { id: 'vmp_abv', title: 'Alkohol % (VMP)', type: 'number', visible: false, niche: false, width: '120px', render: (row) => row.vmp_abv ? `${row.vmp_abv}%` : '-' },
    { id: 'unt_abv', title: 'Alkohol % (Untappd)', type: 'number', visible: true, niche: false, width: '140px', render: (row) => row.unt_abv ? `${row.unt_abv}%` : '-' },
    { id: 'unt_ibu', title: 'Bitterhet (IBU)', type: 'number', visible: false, niche: false, width: '120px', render: (row) => row.unt_ibu || '-' },
    
    { id: 'rating_score', title: 'Rating (Untappd)', type: 'number', visible: true, niche: false, width: '120px', render: (row) => row.rating_score ? `<span class="rating">⭐ ${row.rating_score.toFixed(2)}</span>` : '-' },
    { id: 'bayesian_rating', title: 'Bayesian Rating', type: 'number', visible: false, niche: false, width: '130px', render: (row) => row.bayesian_rating ? `<span class="rating">⭐ ${row.bayesian_rating.toFixed(2)}</span>` : '-' },
    { id: 'rating_count', title: 'Antall Ratinger', type: 'number', visible: false, niche: false, width: '120px', render: (row) => row.rating_count ? row.rating_count.toLocaleString() : '-' },
    
    { id: 'selection', title: 'Utvalg (VMP)', type: 'text', visible: false, niche: false, width: '130px', render: (row) => row.selection || '-' },
    { id: 'packaging', title: 'Emballasje', type: 'text', visible: false, niche: false, width: '120px', render: (row) => row.packaging || '-' },
    { id: 'vintage', title: 'Årgang', type: 'text', visible: false, niche: false, width: '100px', render: (row) => row.vintage || '-' },

    // --- NICHE KOLONNER (niche: true) ---
    { id: 'aroma', title: 'Aroma (VMP)', type: 'text', visible: false, niche: true, width: '200px', render: (row) => row.aroma || '-' },
    { id: 'taste', title: 'Smak (VMP)', type: 'text', visible: false, niche: true, width: '200px', render: (row) => row.taste || '-' },
    { id: 'color', title: 'Farge (VMP)', type: 'text', visible: false, niche: true, width: '150px', render: (row) => row.color || '-' },
    { id: 'method', title: 'Metode (VMP)', type: 'text', visible: false, niche: true, width: '200px', render: (row) => row.method || '-' },
    { id: 'allergens', title: 'Allergener', type: 'text', visible: false, niche: true, width: '150px', render: (row) => row.allergens || '-' },
    { id: 'is_discontinued', title: 'Utgått (VMP)', type: 'none', visible: false, niche: true, width: '100px', render: (row) => row.is_discontinued ? 'Ja' : 'Nei' },
    
    { id: 'in_production', title: 'I Produksjon (Untappd)', type: 'none', visible: false, niche: true, width: '160px', render: (row) => row.in_production === null ? '-' : (row.in_production ? 'Ja' : 'Nei') },
    { id: 'has_community_award', title: 'På Untappd Toppliste', type: 'none', visible: false, niche: false, width: '160px', render: (row) => row.has_community_award ? 'Ja' : 'Nei' },
    { id: 'popularity', title: 'Popularitetsscore', type: 'number', visible: false, niche: true, width: '130px', render: (row) => row.popularity ? row.popularity.toLocaleString() : '-' },
    { id: 'unt_style_description', title: 'Stilbeskrivelse', type: 'text', visible: false, niche: true, width: '250px', render: (row) => row.unt_style_description || '-' },
    
    { id: 'last_synced_unt', title: 'Sist Oppdatert (Lokal)', type: 'text', visible: false, niche: true, width: '150px', render: (row) => row.last_synced_unt ? row.last_synced_unt.split(' ')[0] : '-' },
    { id: 'index_date', title: 'Sist Endret (Untappd)', type: 'text', visible: false, niche: true, width: '150px', render: (row) => row.index_date ? row.index_date.split('T')[0] : '-' },
    { id: 'unt_lat', title: 'Breddegrad (Lat)', type: 'number', visible: false, niche: true, width: '120px', render: (row) => row.unt_lat || '-' },
    { id: 'unt_lng', title: 'Lengdegrad (Lng)', type: 'number', visible: false, niche: true, width: '120px', render: (row) => row.unt_lng || '-' },
    
    { id: 'product_id_vmp', title: 'VMP Varenummer', type: 'text', visible: false, niche: true, width: '120px', render: (row) => row.product_id_vmp },
    { id: 'unt_id', title: 'Untappd Beer ID', type: 'text', visible: false, niche: true, width: '120px', render: (row) => row.unt_id || '-' },
    { id: 'vmp_producer_id', title: 'VMP Produsent ID', type: 'text', visible: false, niche: true, width: '130px', render: (row) => row.vmp_producer_id || '-' },
    { id: 'vmp_category_id', title: 'VMP Kategori ID', type: 'text', visible: false, niche: true, width: '120px', render: (row) => row.vmp_category_id || '-' },
    { id: 'unt_style_id', title: 'Untappd Stil ID', type: 'text', visible: false, niche: true, width: '120px', render: (row) => row.unt_style_id || '-' },
    { id: 'unt_brewery_id', title: 'Untappd Bryggeri ID', type: 'text', visible: false, niche: true, width: '140px', render: (row) => row.unt_brewery_id || '-' },
    
    { id: 'url_vmp', title: 'VMP URL (Rå)', type: 'text', visible: false, niche: true, width: '200px', render: (row) => row.url_vmp ? `<a href="${row.url_vmp}" target="_blank">Lenke</a>` : '-' },
    { id: 'url_unt', title: 'Untappd URL (Rå)', type: 'text', visible: false, niche: true, width: '200px', render: (row) => row.url_unt ? `<a href="${row.url_unt}" target="_blank">Lenke</a>` : '-' },
    { id: 'vmp_image', title: 'VMP Bilde URL', type: 'text', visible: false, niche: true, width: '200px', render: (row) => row.vmp_image || '-' },
    { id: 'url_image', title: 'Untappd Bilde URL', type: 'text', visible: false, niche: true, width: '200px', render: (row) => row.url_image || '-' },
    { id: 'brewery_url', title: 'Bryggeri URL', type: 'text', visible: false, niche: true, width: '200px', render: (row) => row.brewery_url ? `<a href="${row.brewery_url}" target="_blank">Lenke</a>` : '-' },
    { id: 'brewery_label', title: 'Bryggeri Logo URL', type: 'text', visible: false, niche: true, width: '200px', render: (row) => row.brewery_label || '-' }
];

let allBeers = [];
let sortCol = 'match_confidence';
let sortDesc = true;

// Filtrering state
let activeFilters = {
    country: new Set(),
    style: new Set(),
    untStyle: new Set(),
    brewery: new Set(),
    award: new Set(),
    mainCategory: new Set()
};

let colFilters = {}; // Per-kolonne filter states

// DOM Elements
const tableHeader = document.getElementById('tableHeader');
const tableFilters = document.getElementById('tableFilters');
const tableBody = document.getElementById('tableBody');
const mainColumns = document.getElementById('mainColumns');
const nicheColumns = document.getElementById('nicheColumns');
const searchInput = document.getElementById('searchInput');
const filterDiscontinued = document.getElementById('filterDiscontinued');
const filterMatchedOnly = document.getElementById('filterMatchedOnly');
const filterLowMatch = document.getElementById('filterLowMatch');
const statsBar = document.getElementById('statsBar');

const beerModal = document.getElementById('beerModal');
const closeModalBtn = document.getElementById('closeModal');
const modalBody = document.getElementById('modalBody');

async function init() {
    setupColumnToggles();
    renderHeader();
    
    try {
        const response = await fetch('/api/beers');
        allBeers = await response.json();
        // Calculate Bayesian constants (C and m) ONLY for beers with match > 50
        let sumRating = 0;
        let sumCount = 0;
        let numValid = 0;
        
        allBeers.forEach(b => {
            // Sett award_text for filter
            b.award_text = b.has_community_award ? 'Ja' : 'Nei';

            if (b.match_confidence && b.match_confidence > 50 && b.rating_score > 0 && b.rating_count > 0) {
                sumRating += b.rating_score;
                sumCount += b.rating_count;
                numValid++;
            }
        });
        const C = numValid > 0 ? sumRating / numValid : 0;
        const m = numValid > 0 ? sumCount / numValid : 0;

        allBeers.forEach(b => {
            // Bayesian
            if (b.rating_score > 0 && b.rating_count > 0) {
                b.bayesian_rating = (b.rating_count * b.rating_score + m * C) / (b.rating_count + m);
            } else {
                b.bayesian_rating = null;
            }
            // Price per liter
            if (b.price > 0 && b.volume_ml > 0) {
                b.price_per_liter = b.price / (b.volume_ml / 1000);
            } else {
                b.price_per_liter = null;
            }
        });

        
        setupDropdown('dropdownCountry', 'vmp_country', 'country');
        setupDropdown('dropdownStyle', 'vmp_style', 'style');
        setupDropdown('dropdownBrewery', 'unt_brewery', 'brewery');
        setupDropdown('dropdownMainCategory', 'vmp_main_category', 'mainCategory');
        setupDropdown('dropdownUntStyle', 'unt_style', 'untStyle');
        setupDropdown('dropdownAward', 'award_text', 'award');
        
        renderTable();
    } catch (error) {
        statsBar.innerHTML = 'Klarte ikke laste data fra serveren. Feil: ' + error.toString() + ' <br><small>' + error.stack + '</small>';
        console.error(error);
    }

    // Lukk dropdowns ved klikk utenfor
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.custom-dropdown')) {
            document.querySelectorAll('.dropdown-content').forEach(d => d.classList.add('hidden'));
        }
        if (e.target === beerModal) {
            beerModal.classList.add('hidden');
        }
    });

    closeModalBtn.addEventListener('click', () => {
        beerModal.classList.add('hidden');
    });

    // Event listeners
    filterDiscontinued.addEventListener('change', renderTable);
    filterMatchedOnly.addEventListener('change', renderTable);
    if (filterLowMatch) filterLowMatch.addEventListener('change', renderTable);
    
    // Toggle Sidebar
    const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
    const sidebar = document.getElementById('sidebar');
    if (toggleSidebarBtn && sidebar) {
        toggleSidebarBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }
}

function setupDropdown(elementId, dataField, filterKey) {
    const el = document.getElementById(elementId);
    const header = el.querySelector('.dropdown-header');
    const headerText = el.querySelector('.dh-text');
    const content = el.querySelector('.dropdown-content');
    const search = el.querySelector('.dropdown-search');
    const list = el.querySelector('.dropdown-list');
    
    // Hent unike verdier
    const uniqueValues = [...new Set(allBeers.map(b => b[dataField]).filter(Boolean))].sort();
    const defaultText = headerText.textContent;
    
    const updateHeader = () => {
        if (activeFilters[filterKey].size === 0) {
            headerText.textContent = defaultText;
        } else if (activeFilters[filterKey].size === 1) {
            headerText.textContent = [...activeFilters[filterKey]][0];
        } else {
            headerText.textContent = activeFilters[filterKey].size + ' valgt';
        }
    };
    
    const renderList = (searchTerm = '') => {
        list.innerHTML = '';
        
        // Legg til "Fjern filter" valg
        const clearItem = document.createElement('div');
        clearItem.className = 'dropdown-item';
        clearItem.textContent = 'Vis alle';
        if (activeFilters[filterKey].size === 0) clearItem.classList.add('active');
        clearItem.addEventListener('click', () => {
            activeFilters[filterKey].clear();
            updateHeader();
            content.classList.add('hidden');
            renderTable();
            renderFilterChips();
        });
        list.appendChild(clearItem);
        
        const filtered = uniqueValues.filter(v => v.toLowerCase().includes(searchTerm.toLowerCase()));
        filtered.forEach(val => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.textContent = val;
            if (activeFilters[filterKey].has(val)) item.classList.add('active');
            
            item.addEventListener('click', (e) => {
                e.stopPropagation(); // Keep open for multi-select
                if (activeFilters[filterKey].has(val)) {
                    activeFilters[filterKey].delete(val);
                    item.classList.remove('active');
                } else {
                    activeFilters[filterKey].add(val);
                    item.classList.add('active');
                }
                updateHeader();
                renderTable();
                renderFilterChips();
            });
            list.appendChild(item);
        });
    };
    
    renderList();
    
    header.addEventListener('click', (e) => {
        e.stopPropagation();
        const isHidden = content.classList.contains('hidden');
        document.querySelectorAll('.dropdown-content').forEach(d => d.classList.add('hidden')); // Lukk andre
        if (isHidden) {
            content.classList.remove('hidden');
            if (search) {
                search.value = '';
                search.focus();
            }
            renderList();
        }
    });
    
    if (search) {
        search.addEventListener('click', (e) => e.stopPropagation());
        search.addEventListener('input', (e) => {
            renderList(e.target.value);
        });
    }
}
function setupColumnToggles() {
    mainColumns.innerHTML = '';
    nicheColumns.innerHTML = '';
    
    COLUMNS.forEach((col, index) => {
        const label = document.createElement('label');
        label.className = 'checkbox-label';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = col.visible;
        checkbox.addEventListener('change', (e) => {
            COLUMNS[index].visible = e.target.checked;
            renderHeader();
            renderTable();
        });

        
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(col.title));
        
        if (col.niche) {
            nicheColumns.appendChild(label);
        } else {
            mainColumns.appendChild(label);
        }
    });
}

function renderHeader() {
    renderHeaderRow();
    renderFilterRow();
}

function renderHeaderRow() {
    tableHeader.innerHTML = '';
    COLUMNS.forEach(col => {
        if (!col.visible) return;
        
        const th = document.createElement('th');
        th.style.width = col.width;
        th.style.minWidth = col.width;
        th.style.maxWidth = col.width;
        
        // Wrapper for teksten
        const content = document.createElement('span');
        let icon = '';
        if (col.type === 'number') {
            if (sortCol === col.id) {
                icon = sortDesc ? ' ↓' : ' ↑';
            } else {
                icon = ' ↕';
            }
            content.addEventListener('click', () => {
                if (sortCol === col.id) {
                    sortDesc = !sortDesc;
                } else {
                    sortCol = col.id;
                    sortDesc = true; 
                }
                renderHeaderRow(); // Only rerender the top row so input focus is kept
                renderTable();
            });
        }
        
        content.textContent = col.title + icon;
        th.appendChild(content);

        // Resize-håndtak
        const resizer = document.createElement('div');
        resizer.className = 'resizer';
        th.appendChild(resizer);
        createResizableColumn(th, resizer);
        
        tableHeader.appendChild(th);
    });
}

function renderFilterRow() {
    tableFilters.innerHTML = '';
    
    // Sett riktig top-offset dynamisk for å unngå gap mellom header radene
    requestAnimationFrame(() => {
        const headerHeight = document.getElementById('tableHeader').getBoundingClientRect().height;
        Array.from(tableFilters.children).forEach(th => {
            th.style.top = (headerHeight - 1) + 'px'; // -1px for å overlappe borderen og sikre null gap
        });
    });

    COLUMNS.forEach(col => {
        if (!col.visible) return;
        
        const th = document.createElement('th');
        
        if (col.type === 'text') {
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'filter-input-text';
            input.placeholder = 'Søk...';
            input.value = colFilters[col.id] || '';
            input.addEventListener('input', (e) => {
                colFilters[col.id] = e.target.value;
                renderTable();
            });
            th.appendChild(input);
        } else if (col.type === 'number') {
            const group = document.createElement('div');
            group.className = 'filter-input-number-group';
            
            const minInput = document.createElement('input');
            minInput.type = 'number';
            minInput.className = 'filter-input-number';
            minInput.placeholder = 'Min';
            minInput.value = (colFilters[col.id] && colFilters[col.id].min !== null) ? colFilters[col.id].min : '';
            minInput.addEventListener('input', (e) => {
                if (!colFilters[col.id]) colFilters[col.id] = { min: null, max: null };
                colFilters[col.id].min = e.target.value === '' ? null : Number(e.target.value);
                renderTable();
            });
            
            const maxInput = document.createElement('input');
            maxInput.type = 'number';
            maxInput.className = 'filter-input-number';
            maxInput.placeholder = 'Max';
            maxInput.value = (colFilters[col.id] && colFilters[col.id].max !== null) ? colFilters[col.id].max : '';
            maxInput.addEventListener('input', (e) => {
                if (!colFilters[col.id]) colFilters[col.id] = { min: null, max: null };
                colFilters[col.id].max = e.target.value === '' ? null : Number(e.target.value);
                renderTable();
            });
            
            group.appendChild(minInput);
            group.appendChild(maxInput);
            th.appendChild(group);
        }
        
        tableFilters.appendChild(th);
    });
}

function createResizableColumn(th, resizer) {
    let x = 0;
    let w = 0;

    const mouseDownHandler = function (e) {
        x = e.clientX;
        const styles = window.getComputedStyle(th);
        w = parseInt(styles.width, 10);

        document.addEventListener('mousemove', mouseMoveHandler);
        document.addEventListener('mouseup', mouseUpHandler);
        resizer.classList.add('resizing');
    };

    const mouseMoveHandler = function (e) {
        const dx = e.clientX - x;
        th.style.minWidth = `${w + dx}px`;
        th.style.maxWidth = `${w + dx}px`;
        th.style.width = `${w + dx}px`;
    };

    const mouseUpHandler = function () {
        document.removeEventListener('mousemove', mouseMoveHandler);
        document.removeEventListener('mouseup', mouseUpHandler);
        resizer.classList.remove('resizing');
    };

    resizer.addEventListener('mousedown', mouseDownHandler);
}

function getFilteredAndSortedData() {
    const hideDiscontinued = filterDiscontinued.checked;
    const hideUnmatched = filterMatchedOnly.checked;
    const showOnlyLowMatch = filterLowMatch && filterLowMatch.checked;

    let filtered = allBeers.filter(beer => {
        // Avanserte dropdowns
        if (activeFilters.country.size > 0 && !activeFilters.country.has(beer.vmp_country)) return false;
        if (activeFilters.style.size > 0 && !activeFilters.style.has(beer.vmp_style)) return false;
        if (activeFilters.untStyle.size > 0 && !activeFilters.untStyle.has(beer.unt_style)) return false;
        if (activeFilters.brewery.size > 0 && !activeFilters.brewery.has(beer.unt_brewery)) return false;
        if (activeFilters.mainCategory.size > 0 && !activeFilters.mainCategory.has(beer.vmp_main_category)) return false;
        
        if (hideDiscontinued && beer.is_discontinued) return false;
        
        if (showOnlyLowMatch) {
            if (beer.match_confidence !== null && beer.match_confidence > 50) return false;
        } else {
            if (hideUnmatched && (!beer.match_confidence || beer.match_confidence < 0.1)) return false;
        }
        
        // Per-kolonne filtre
        for (const col of COLUMNS) {
            const filterVal = colFilters[col.id];
            if (!filterVal) continue;
            
            const cellVal = beer[col.id];
            
            if (col.type === 'text') {
                if (typeof filterVal === 'string' && filterVal.trim() !== '') {
                    if (!cellVal || !cellVal.toString().toLowerCase().includes(filterVal.toLowerCase())) {
                        return false;
                    }
                }
            } else if (col.type === 'number') {
                if (filterVal.min !== null || filterVal.max !== null) {
                    if (cellVal === null || cellVal === undefined) return false;
                    if (filterVal.min !== null && cellVal < filterVal.min) return false;
                    if (filterVal.max !== null && cellVal > filterVal.max) return false;
                }
            }
        }
        
        return true;
    });

    filtered.sort((a, b) => {
        let valA = a[sortCol];
        let valB = b[sortCol];

        if (valA === null || valA === undefined) valA = '';
        if (valB === null || valB === undefined) valB = '';

        if (typeof valA === 'string') valA = valA.toLowerCase();
        if (typeof valB === 'string') valB = valB.toLowerCase();

        if (valA < valB) return sortDesc ? 1 : -1;
        if (valA > valB) return sortDesc ? -1 : 1;
        return 0;
    });

    return filtered;
}

function renderTable() {
    const data = getFilteredAndSortedData();
    tableBody.innerHTML = '';

    statsBar.innerHTML = `Viser <strong>${data.length}</strong> av totalt ${allBeers.length} produkter.`;

    data.forEach(beer => {
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        tr.addEventListener('click', () => openModal(beer));
        
        COLUMNS.forEach(col => {
            if (!col.visible) return;
            const td = document.createElement('td');
            td.innerHTML = col.render(beer);
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    });
    renderFilterChips();
}

function renderFilterChips() {
    const activeFiltersContainer = document.getElementById('activeFiltersContainer');
    if (!activeFiltersContainer) return;
    activeFiltersContainer.innerHTML = '';
    
    const addChip = (text, onRemove) => {
        const chip = document.createElement('div');
        chip.className = 'filter-chip';
        chip.innerHTML = `<span>${text}</span> <span class="close-icon">&times;</span>`;
        chip.addEventListener('click', () => {
            onRemove();
            renderFilterChips(); // Update chips visually
            renderTable(); // Update table
        });
        activeFiltersContainer.appendChild(chip);
    };

    const dropdownMappings = {
        mainCategory: { label: 'Hovedkategori', element: 'dropdownMainCategory', defaultText: 'Hovedkategori' },
        style: { label: 'Stil', element: 'dropdownStyle', defaultText: 'Stil' },
        untStyle: { label: 'Understil', element: 'dropdownUntStyle', defaultText: 'Understil' },
        country: { label: 'Land', element: 'dropdownCountry', defaultText: 'Land' },
        brewery: { label: 'Bryggeri', element: 'dropdownBrewery', defaultText: 'Bryggeri' },
        award: { label: 'Toppliste', element: 'dropdownAward', defaultText: 'Toppliste' }
    };

    for (const key in dropdownMappings) {
        if (activeFilters[key].size > 0) {
            activeFilters[key].forEach(val => {
                addChip(`${dropdownMappings[key].label}: ${val}`, () => {
                    activeFilters[key].delete(val);
                    // Oppdater dropdown header text
                    const el = document.getElementById(dropdownMappings[key].element).querySelector('.dh-text');
                    if (activeFilters[key].size === 0) {
                        el.textContent = dropdownMappings[key].defaultText;
                    } else if (activeFilters[key].size === 1) {
                        el.textContent = [...activeFilters[key]][0];
                    } else {
                        el.textContent = activeFilters[key].size + ' valgt';
                    }
                });
            });
        }
    }
    
    // Column Filters
    for (const [colId, filterVal] of Object.entries(colFilters)) {
        if (!filterVal) continue;
        const colDef = COLUMNS.find(c => c.id === colId);
        if (!colDef) continue;
        
        if (colDef.type === 'text' && filterVal.trim() !== '') {
            addChip(`${colDef.title}: "${filterVal}"`, () => {
                delete colFilters[colId];
                renderFilterRow(); // For å fjerne verdien fra input-feltet
                renderTable();
            });
        } else if (colDef.type === 'number') {
            if (filterVal.min !== null || filterVal.max !== null) {
                let text = `${colDef.title}: `;
                if (filterVal.min !== null && filterVal.max !== null) text += `${filterVal.min} - ${filterVal.max}`;
                else if (filterVal.min !== null) text += `Min ${filterVal.min}`;
                else text += `Max ${filterVal.max}`;
                
                addChip(text, () => {
                    delete colFilters[colId];
                    renderFilterRow();
                    renderTable();
                });
            }
        }
    }
}

function openModal(beer) {
    const vmpUrl = `https://www.vinmonopolet.no/p/${beer.product_id_vmp}`;
    const vmpUrlHtml = `<a href="${vmpUrl}" target="_blank" onclick="event.stopPropagation()" style="margin-left:10px; font-size:0.85rem;">Se på Vinmonopolet 🍇</a>`;
    const untUrlHtml = beer.url_unt ? `<a href="${beer.url_unt}" target="_blank" onclick="event.stopPropagation()" style="margin-left:10px; font-size:0.85rem;">Se på Untappd 🍺</a>` : '';
    
    // Fallback logikk for bilde
    let headerImage = '';
    if (beer.vmp_image) {
        headerImage = `<img src="${beer.vmp_image}" alt="VMP image">`;
    } else if (beer.url_image && beer.url_image !== 'https://assets.untappd.com/') {
        headerImage = `<img src="${beer.url_image}" alt="Beer image">`;
    }

    // Pars Untappd Utmerkelser (JSON)
    let awardsHtml = '';
    if (beer.community_awards && beer.community_awards !== '[]') {
        try {
            const awards = JSON.parse(beer.community_awards);
            if (Array.isArray(awards) && awards.length > 0) {
                const awardList = awards.map(a => {
                    let rankEmoji = '⭐';
                    let rankText = a.style_rank ? `${a.style_rank}. plass` : 'Toppliste';
                    if (a.style_rank === 1) rankEmoji = '🥇';
                    else if (a.style_rank === 2) rankEmoji = '🥈';
                    else if (a.style_rank === 3) rankEmoji = '🥉';
                    
                    const region = a.region || 'Ukjent sted';
                    const year = a.year || '';
                    const style = beer.unt_style || 'Ukjent stil';
                    
                    return `
                        <li style="margin-bottom: 12px; background: var(--bg-dark); padding: 10px; border-radius: 6px; border: 1px solid var(--border);">
                            <div style="font-size: 1.1rem; color: var(--text-primary); margin-bottom: 4px;">
                                ${rankEmoji} <strong>${rankText}</strong>
                            </div>
                            <div style="color: var(--text-secondary); font-size: 0.95rem;">
                                <strong>Stil:</strong> ${style}
                            </div>
                            <div style="color: var(--text-secondary); font-size: 0.95rem;">
                                <strong>Hvor:</strong> ${region} ${year ? `(${year})` : ''}
                            </div>
                        </li>
                    `;
                }).join('');
                
                awardsHtml = `
                    <div class="modal-section" style="margin-top:1.5rem; border-top:1px solid var(--border); padding-top:1.5rem;">
                        <h4 style="border:none; margin-bottom:1rem; color:var(--accent);">Untappd Utmerkelser</h4>
                        <ul style="list-style-type:none; padding:0; margin:0;">
                            ${awardList}
                        </ul>
                    </div>
                `;
            }
        } catch(e) {
            console.error("Could not parse awards", e);
        }
    }
    
    let html = `
        <div class="modal-header-container">
            ${headerImage}
            <div>
                <h2 style="color:var(--text-primary); margin-bottom:0.5rem;">${beer.unt_name || beer.vmp_name}</h2>
                <div style="color:var(--text-secondary); font-size:1.1rem;">
                    ${beer.unt_brewery || beer.vmp_brewery || 'Ukjent bryggeri'} 
                    ${beer.rating_score ? `<span class="rating" style="margin-left:15px;">⭐ ${beer.rating_score.toFixed(2)}</span>` : ''}
                </div>
            </div>
        </div>
        
        <div class="modal-grid">
            <div class="modal-section">
                <h4>Vinmonopolet Data ${vmpUrlHtml}</h4>
                <div class="modal-info-row"><div class="modal-info-label">VMP Navn:</div><div class="modal-info-value">${beer.vmp_name}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Bryggeri:</div><div class="modal-info-value">${beer.vmp_brewery || '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Land:</div><div class="modal-info-value">${beer.vmp_country || '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Hovedkategori:</div><div class="modal-info-value">${beer.vmp_main_category || '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Stil:</div><div class="modal-info-value">${beer.vmp_style || '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Pris:</div><div class="modal-info-value">${beer.price ? beer.price.toFixed(2) + ' kr' : '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Volum:</div><div class="modal-info-value">${beer.volume_ml ? beer.volume_ml + ' ml' : '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Pris pr. liter:</div><div class="modal-info-value">${beer.price_per_liter ? beer.price_per_liter.toFixed(2) + ' kr/l' : '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">ABV:</div><div class="modal-info-value">${beer.vmp_abv ? beer.vmp_abv + '%' : '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Årgang:</div><div class="modal-info-value">${beer.vintage || '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Utvalg:</div><div class="modal-info-value">${beer.selection || '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Emballasje:</div><div class="modal-info-value">${beer.packaging || '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">VMP ID:</div><div class="modal-info-value">${beer.product_id_vmp}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Utgått:</div><div class="modal-info-value" style="color:${beer.is_discontinued ? '#ef4444' : 'inherit'}">${beer.is_discontinued ? 'Ja' : 'Nei'}</div></div>
            </div>

            <div class="modal-section">
                <h4>Untappd Data ${untUrlHtml}</h4>
                <div class="modal-info-row"><div class="modal-info-label">Match Score:</div><div class="modal-info-value" style="color:${beer.match_confidence > 75 ? '#22c55e' : 'var(--accent)'}">${beer.match_confidence ? beer.match_confidence.toFixed(1) + '%' : 'Ingen match'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Untappd Navn:</div><div class="modal-info-value">${beer.unt_name || '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Bryggeri:</div><div class="modal-info-value">${beer.unt_brewery || '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Understil:</div><div class="modal-info-value">${beer.unt_style || '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">ABV:</div><div class="modal-info-value">${beer.unt_abv ? beer.unt_abv + '%' : '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">IBU:</div><div class="modal-info-value">${beer.unt_ibu || '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Rating:</div><div class="modal-info-value">${beer.rating_score ? beer.rating_score.toFixed(2) + ' (' + beer.rating_count.toLocaleString() + ' vurderinger)' : '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Bayesian Rating:</div><div class="modal-info-value">${beer.bayesian_rating ? beer.bayesian_rating.toFixed(2) : '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Popularitet:</div><div class="modal-info-value">${beer.popularity ? beer.popularity.toLocaleString() : '-'}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">I Produksjon:</div><div class="modal-info-value">${beer.in_production === null ? '-' : (beer.in_production ? 'Ja' : 'Nei')}</div></div>
                <div class="modal-info-row"><div class="modal-info-label">Sist synkronisert:</div><div class="modal-info-value">${beer.last_synced_unt ? beer.last_synced_unt.split(' ')[0] : '-'}</div></div>
                
                ${beer.unt_description ? `<div class="modal-desc">"${beer.unt_description}"</div>` : ''}
            </div>
        </div>
        
        <div class="modal-section" style="margin-top:2rem; border-top:1px solid var(--border); padding-top:1rem;">
            <h4 style="border:none; margin-bottom:0.5rem;">Smaksprofil (VMP)</h4>
            <div class="modal-info-row"><div class="modal-info-label">Aroma:</div><div class="modal-info-value">${beer.aroma || '-'}</div></div>
            <div class="modal-info-row"><div class="modal-info-label">Smak:</div><div class="modal-info-value">${beer.taste || '-'}</div></div>
            <div class="modal-info-row"><div class="modal-info-label">Farge:</div><div class="modal-info-value">${beer.color || '-'}</div></div>
            <div class="modal-info-row"><div class="modal-info-label">Metode:</div><div class="modal-info-value">${beer.method || '-'}</div></div>
            <div class="modal-info-row"><div class="modal-info-label">Allergener:</div><div class="modal-info-value">${beer.allergens || '-'}</div></div>
        </div>
        
                ${awardsHtml}

        <details style="margin-top:2rem; border-top:1px solid var(--border); padding-top:1rem; cursor: pointer;">
            <summary style="font-weight:bold; color:var(--text-secondary); outline:none; padding: 0.5rem 0;">Vis Niche Data (Rå ID-er og systeminfo) ▾</summary>
            <div style="margin-top: 1rem; cursor: text; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; cursor: auto;">
                <div class="modal-section" style="margin: 0; padding: 1rem; background: var(--bg-dark); border-radius: 6px;">
                    <h5 style="margin-top:0; margin-bottom: 10px; color:var(--text-secondary);">ID-er</h5>
                    <div class="modal-info-row"><div class="modal-info-label">VMP Varenummer:</div><div class="modal-info-value">${beer.product_id_vmp}</div></div>
                    <div class="modal-info-row"><div class="modal-info-label">Untappd Beer ID:</div><div class="modal-info-value">${beer.unt_id || '-'}</div></div>
                    <div class="modal-info-row"><div class="modal-info-label">VMP Prod. ID:</div><div class="modal-info-value">${beer.vmp_producer_id || '-'}</div></div>
                    <div class="modal-info-row"><div class="modal-info-label">VMP Kat. ID:</div><div class="modal-info-value">${beer.vmp_category_id || '-'}</div></div>
                    <div class="modal-info-row"><div class="modal-info-label">Untappd Stil ID:</div><div class="modal-info-value">${beer.unt_style_id || '-'}</div></div>
                    <div class="modal-info-row"><div class="modal-info-label">Unt Bryggeri ID:</div><div class="modal-info-value">${beer.unt_brewery_id || '-'}</div></div>
                </div>
                <div class="modal-section" style="margin: 0; padding: 1rem; background: var(--bg-dark); border-radius: 6px;">
                    <h5 style="margin-top:0; margin-bottom: 10px; color:var(--text-secondary);">System Data & Datoer</h5>
                    <div class="modal-info-row"><div class="modal-info-label">Popularitetsscore:</div><div class="modal-info-value">${beer.popularity ? beer.popularity.toLocaleString() : '-'}</div></div>
                    <div class="modal-info-row"><div class="modal-info-label">Breddegrad (Lat):</div><div class="modal-info-value">${beer.unt_lat || '-'}</div></div>
                    <div class="modal-info-row"><div class="modal-info-label">Lengdegrad (Lng):</div><div class="modal-info-value">${beer.unt_lng || '-'}</div></div>
                    <div class="modal-info-row"><div class="modal-info-label">Sist Endret (Unt):</div><div class="modal-info-value">${beer.index_date || '-'}</div></div>
                    <div class="modal-info-row"><div class="modal-info-label">Sist Oppdatert (Lok):</div><div class="modal-info-value">${beer.last_synced_unt || '-'}</div></div>
                    <div class="modal-info-row"><div class="modal-info-label" style="min-width: 120px;">Stilbeskrivelse:</div><div class="modal-info-value" style="font-size: 0.8rem; line-height:1.2;">${beer.unt_style_description || '-'}</div></div>
                </div>
                <div class="modal-section" style="margin: 0; padding: 1rem; background: var(--bg-dark); border-radius: 6px; grid-column: 1 / -1;">
                    <h5 style="margin-top:0; margin-bottom: 10px; color:var(--text-secondary);">Rå Lenker (Klikkbare)</h5>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div class="modal-info-row"><div class="modal-info-label">VMP URL (Rå):</div><div class="modal-info-value">${beer.url_vmp ? `<a href="${beer.url_vmp}" target="_blank" style="color:var(--accent);">Gå til side</a>` : '-'}</div></div>
                        <div class="modal-info-row"><div class="modal-info-label">Untappd URL (Rå):</div><div class="modal-info-value">${beer.url_unt ? `<a href="${beer.url_unt}" target="_blank" style="color:var(--accent);">Gå til side</a>` : '-'}</div></div>
                        <div class="modal-info-row"><div class="modal-info-label">VMP Bilde URL:</div><div class="modal-info-value">${beer.vmp_image ? `<a href="${beer.vmp_image}" target="_blank" style="color:var(--accent);">Se bilde</a>` : '-'}</div></div>
                        <div class="modal-info-row"><div class="modal-info-label">Untappd Bilde URL:</div><div class="modal-info-value">${beer.url_image && beer.url_image !== 'https://assets.untappd.com/' ? `<a href="${beer.url_image}" target="_blank" style="color:var(--accent);">Se bilde</a>` : '-'}</div></div>
                        <div class="modal-info-row"><div class="modal-info-label">Bryggeri URL:</div><div class="modal-info-value">${beer.brewery_url ? `<a href="${beer.brewery_url}" target="_blank" style="color:var(--accent);">Gå til side</a>` : '-'}</div></div>
                        <div class="modal-info-row"><div class="modal-info-label">Bryggeri Logo URL:</div><div class="modal-info-value">${beer.brewery_label ? `<a href="${beer.brewery_label}" target="_blank" style="color:var(--accent);">Se logo</a>` : '-'}</div></div>
                    </div>
                </div>
            </div>
        </details>

    `;
    
    modalBody.innerHTML = html;
    beerModal.classList.remove('hidden');
}

// Start appen
init();
