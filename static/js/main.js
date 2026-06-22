document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    fetchFacilities();
    initModalEvents();
});

let mapInstance = null;
let markers = [];
let userCredits = 50;
let voucherCredits = 50;
let currentSelectedFac = null;
let currentUserId = null;

function initAuth() {
    const savedUserId = localStorage.getItem('currentUserId');
    const loginOverlay = document.getElementById('login-overlay');
    const loginBtn = document.getElementById('btn-login');
    const loginInput = document.getElementById('login-id');

    if (savedUserId) {
        currentUserId = savedUserId;
        loginOverlay.classList.add('hidden');
        loadUserCredits();
        updateUserUI();
    } else {
        loginInput.focus();
    }

    loginBtn.addEventListener('click', handleLogin);
    loginInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleLogin();
    });
}

function handleLogin() {
    const loginInput = document.getElementById('login-id');
    const userId = loginInput.value.trim();
    if (!userId) return;

    currentUserId = userId;
    localStorage.setItem('currentUserId', currentUserId);
    
    // Initialize credits if not exists
    if (!localStorage.getItem('userCredits')) {
        localStorage.setItem('userCredits', '50');
    }
    if (!localStorage.getItem('voucherCredits')) {
        localStorage.setItem('voucherCredits', '50');
    }
    
    loadUserCredits();
    updateUserUI();

    const loginOverlay = document.getElementById('login-overlay');
    loginOverlay.classList.add('hidden');
}

function loadUserCredits() {
    const savedCredits = localStorage.getItem('userCredits');
    if (savedCredits) {
        userCredits = parseInt(savedCredits, 10);
    } else {
        userCredits = 50;
        localStorage.setItem('userCredits', '50');
    }
    
    const savedVoucher = localStorage.getItem('voucherCredits');
    if (savedVoucher) {
        voucherCredits = parseInt(savedVoucher, 10);
    } else {
        voucherCredits = 50;
        localStorage.setItem('voucherCredits', '50');
    }
    
    document.getElementById('my-credits-display').innerHTML = `${userCredits} 💳`;
    document.getElementById('my-voucher-display').innerHTML = `${voucherCredits} 🎫`;
}

function updateUserUI() {
    const greeting = document.getElementById('user-greeting');
    greeting.textContent = `Hello, ${currentUserId}님!`;
    greeting.style.display = 'block';
}


async function fetchFacilities() {
    try {
        const response = await fetch('/api/facilities');
        const data = await response.json();
        
        if(data.success) {
            renderFacilityList(data.data);
            initMap(data.data);
        }
    } catch (error) {
        console.error("Error fetching facilities:", error);
        document.getElementById('facility-list').innerHTML = `
            <div class="loading-state">
                <p>데이터를 불러오는데 실패했습니다.</p>
            </div>
        `;
    }
}

function renderFacilityList(facilities) {
    const container = document.getElementById('facility-list');
    container.innerHTML = ''; // clear loading

    facilities.forEach((fac, index) => {
        const card = document.createElement('div');
        card.className = 'facility-card';
        card.style.animation = `fadeIn 0.5s ease forwards ${index * 0.1}s`;
        card.style.opacity = '0';
        
        // Define color based on status
        let barColor = '#10b981'; // 쾌적
        if (fac.status_message === '혼잡') barColor = '#ef4444';
        else if (fac.status_message === '보통') barColor = '#3b82f6';

        // Append badge for public facility
        let badgeHtml = '';
        if (fac.is_public) {
            badgeHtml = `<span style="background:#1e3a8a; color:white; padding:2px 6px; border-radius:4px; font-size:10px; margin-left:6px;">공공시설</span>`;
        }

        card.innerHTML = `
            <img src="${fac.image}" alt="${fac.facility_name}" class="facility-img">
            <div class="facility-info">
                <h3>${fac.facility_name} ${badgeHtml}</h3>
                <div style="font-size: 12px; color: var(--text-secondary);">
                    예측 혼잡도: ${fac.predicted_congestion}% 
                    <div class="congestion-bar-bg">
                        <div class="congestion-bar-fill" style="width: ${fac.predicted_congestion}%; background: ${barColor};"></div>
                    </div>
                </div>
                <div class="facility-meta">
                    <span class="status-badge ${fac.status_message}">${fac.status_message}</span>
                    <span class="credit-badge">${fac.required_credit} 크레딧</span>
                </div>
            </div>
        `;
        
        // Click to pan map and open modal
        card.addEventListener('click', () => {
            if(mapInstance) {
                mapInstance.morph(new naver.maps.LatLng(fac.latitude, fac.longitude), 16);
            }
            openBookingModal(fac);
        });

        container.appendChild(card);
    });
}

// Add animation keyframe to document
const styleSheet = document.createElement("style");
styleSheet.innerText = `
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;
document.head.appendChild(styleSheet);


function initMap(facilities) {
    if (typeof naver === 'undefined') {
        console.warn("Naver Map API not loaded.");
        return;
    }

    const container = document.getElementById('map');
    
    // Calculate center
    const avgLat = facilities.reduce((sum, fac) => sum + fac.latitude, 0) / facilities.length;
    const avgLng = facilities.reduce((sum, fac) => sum + fac.longitude, 0) / facilities.length;

    // Initialize Naver map (스포티파이 다크 모드에 어울리는 옵션 적용)
    mapInstance = new naver.maps.Map(container, {
        center: new naver.maps.LatLng(avgLat, avgLng),
        zoom: 14,
        mapTypeId: naver.maps.MapTypeId.NORMAL
    });

    facilities.forEach(fac => {
        // Map Emoji
        let emoji = '📍';
        const name = fac.facility_name;
        if (name.includes('축구') || name.includes('풋살')) emoji = '⚽';
        else if (name.includes('수영')) emoji = '🏊‍♂️';
        else if (name.includes('요가') || name.includes('필라테스')) emoji = '🧘‍♀️';
        else if (name.includes('복싱') || name.includes('격투')) emoji = '🥊';
        else if (name.includes('유도') || name.includes('태권') || name.includes('검도') || name.includes('주짓수')) emoji = '🥋';
        else if (name.includes('탁구')) emoji = '🏓';
        else if (name.includes('클라이밍')) emoji = '🧗';
        else if (name.includes('배드민턴') || name.includes('테니스')) emoji = '🏸';
        else if (name.includes('체육') || name.includes('스포츠') || name.includes('짐')) emoji = '🏋️‍♂️';

        // 네이버 지도 커스텀 HTML 마커 (스포티파이 디자인 유지)
        const markerHtml = `
            <div class="custom-spotify-marker-container">
                <div class="spotify-marker" style="width:32px; height:32px; font-size:16px;">${emoji}</div>
            </div>
        `;

        const marker = new naver.maps.Marker({
            position: new naver.maps.LatLng(fac.latitude, fac.longitude),
            map: mapInstance,
            icon: {
                content: markerHtml,
                size: new naver.maps.Size(32, 32),
                anchor: new naver.maps.Point(16, 16)
            }
        });
        
        markers.push(marker);

        // Add info window
        let colorHex = '#10b981';
        if (fac.status_message === '혼잡') colorHex = '#ef4444';
        else if (fac.status_message === '보통') colorHex = '#3b82f6';

        const iwContent = `
            <div class="custom-infowindow" style="background:var(--card-bg); padding:14px 16px; border-radius:8px; box-shadow:0 8px 24px rgba(0,0,0,0.5); min-width:auto; color:var(--text-primary); border:none;">
                <h4 style="margin:0 0 5px 0; font-size:14px; font-weight:700;">${fac.facility_name}</h4>
                <p style="font-size:12px; margin:0; color:var(--text-secondary);">${fac.status_message} (${fac.predicted_congestion}%)</p>
                <p style="font-size:14px; margin:5px 0 0 0; font-weight:bold; color:${colorHex};">${fac.required_credit} 크레딧</p>
            </div>
        `;

        const infoWindow = new naver.maps.InfoWindow({
            content: iwContent,
            borderWidth: 0,
            backgroundColor: "transparent",
            disableAnchor: true,
            pixelOffset: new naver.maps.Point(0, -10)
        });

        // 네이버 지도는 click 이벤트를 리스너로 등록
        naver.maps.Event.addListener(marker, 'click', function() {
            // 다른 열려있는 정보창이 있다면 닫고 새로 열기
            if (infoWindow.getMap()) {
                infoWindow.close();
            } else {
                infoWindow.open(mapInstance, marker);
            }
            openBookingModal(fac);
        });
    });
}
function initModalEvents() {
    const cancelBtn = document.getElementById('btn-cancel');
    const confirmBtn = document.getElementById('btn-confirm');
    const voucherBtn = document.getElementById('btn-voucher');
    const modalOverlay = document.getElementById('booking-modal');

    cancelBtn.addEventListener('click', closeBookingModal);
    
    // Close modal when clicking outside the card
    modalOverlay.addEventListener('click', (e) => {
        if(e.target === modalOverlay) {
            closeBookingModal();
        }
    });

    confirmBtn.addEventListener('click', processReservation);
    voucherBtn.addEventListener('click', processVoucherReservation);
}

function openBookingModal(fac) {
    currentSelectedFac = fac;
    document.getElementById('modal-fac-name').textContent = fac.facility_name;
    document.getElementById('modal-req-credit').textContent = fac.required_credit;
    
    // Show voucher button only if public facility
    const voucherBtn = document.getElementById('btn-voucher');
    if (fac.is_public) {
        voucherBtn.style.display = 'flex';
        voucherBtn.style.alignItems = 'center';
        voucherBtn.style.justifyContent = 'center';
    } else {
        voucherBtn.style.display = 'none';
    }

    const modal = document.getElementById('booking-modal');
    modal.classList.remove('hidden');
}

function closeBookingModal() {
    const modal = document.getElementById('booking-modal');
    modal.classList.add('hidden');
    currentSelectedFac = null;
}

function processReservation() {
    if(!currentSelectedFac) return;

    const reqCredit = currentSelectedFac.required_credit;
    
    if(userCredits >= reqCredit) {
        // Deduct general credits
        userCredits -= reqCredit;
        localStorage.setItem('userCredits', userCredits.toString());
        document.getElementById('my-credits-display').innerHTML = `${userCredits} 💳`;
        
        closeBookingModal();
        showToast(`성공적으로 일반 결제되었습니다! (잔여 일반: ${userCredits})`);
    } else {
        alert("일반 크레딧이 부족합니다!");
        closeBookingModal();
    }
}

function processVoucherReservation() {
    if(!currentSelectedFac || !currentSelectedFac.is_public) return;

    let reqCredit = currentSelectedFac.required_credit;
    let deductedVoucher = 0;
    let deductedGeneral = 0;

    // Deduct from voucher first
    if (voucherCredits >= reqCredit) {
        voucherCredits -= reqCredit;
        deductedVoucher = reqCredit;
        reqCredit = 0;
    } else {
        deductedVoucher = voucherCredits;
        reqCredit -= voucherCredits;
        voucherCredits = 0;
    }

    // Deduct remaining from general
    if (reqCredit > 0) {
        if (userCredits >= reqCredit) {
            userCredits -= reqCredit;
            deductedGeneral = reqCredit;
        } else {
            alert("바우처와 일반 크레딧을 합쳐도 결제에 부족합니다!");
            closeBookingModal();
            return;
        }
    }

    // Save state
    localStorage.setItem('voucherCredits', voucherCredits.toString());
    localStorage.setItem('userCredits', userCredits.toString());
    document.getElementById('my-voucher-display').innerHTML = `${voucherCredits} 🎫`;
    document.getElementById('my-credits-display').innerHTML = `${userCredits} 💳`;

    closeBookingModal();
    showToast(`바우처 결제 완료! (바우처 차감: ${deductedVoucher}, 일반 차감: ${deductedGeneral})`);
}

function showToast(message) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<span>✅</span> ${message}`;
    
    container.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => {
            if(container.contains(toast)) {
                container.removeChild(toast);
            }
        }, 300); // Wait for fade-out animation
    }, 3000);
}
