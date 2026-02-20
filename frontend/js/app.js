// ============================================
        // API CONFIGURATION
        // ============================================
        const API_BASE_URL = 'https://accommodative-dusti-subpetiolate.ngrok-free.dev/api';

        // ============================================
        // TOAST NOTIFICATION SYSTEM
        // ============================================
        function showToast(message, type = 'info', title = '') {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            
            // Set default titles based on type
            if (!title) {
                const titles = {
                    success: 'Success',
                    error: 'Error',
                    info: 'Info',
                    warning: 'Warning'
                };
                title = titles[type] || 'Notification';
            }
            
            // Icons for each type
            const icons = {
                success: '<svg class="toast-icon success" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>',
                error: '<svg class="toast-icon error" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>',
                info: '<svg class="toast-icon info" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
                warning: '<svg class="toast-icon warning" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>'
            };
            
            toast.innerHTML = `
                ${icons[type]}
                <div class="toast-content">
                    <div class="toast-title">${title}</div>
                    <div class="toast-message">${message}</div>
                </div>
                <button class="toast-close" onclick="this.parentElement.remove()">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            `;
            
            container.appendChild(toast);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                toast.classList.add('removing');
                setTimeout(() => toast.remove(), 300);
            }, 5000);
        }

        // ============================================
        // SESSION MANAGEMENT
        // ============================================
        const Auth = {
            getSessionId() {
                return localStorage.getItem('session_id');
            },
            
            setSessionId(sessionId) {
                localStorage.setItem('session_id', sessionId);
            },
            
            getUser() {
                const user = localStorage.getItem('user');
                return user ? JSON.parse(user) : null;
            },
            
            setUser(user) {
                localStorage.setItem('user', JSON.stringify(user));
            },
            
            logout() {
                localStorage.removeItem('session_id');
                localStorage.removeItem('user');
            },
            
            isLoggedIn() {
                return !!this.getSessionId();
            }
        };

        // ============================================
        // PASSWORD TOGGLE FUNCTION
        // ============================================
        function togglePassword(inputId, button) {
            const input = document.getElementById(inputId);
            const eyeIcon = button.querySelector('.eye-icon');
            const eyeOffIcon = button.querySelector('.eye-off-icon');
            
            if (input.type === 'password') {
                input.type = 'text';
                eyeIcon.style.display = 'none';
                eyeOffIcon.style.display = 'block';
            } else {
                input.type = 'password';
                eyeIcon.style.display = 'block';
                eyeOffIcon.style.display = 'none';
            }
        }

        // ============================================
        // API FUNCTIONS
        // ============================================
        async function apiRequest(endpoint, options = {}) {
            const sessionId = Auth.getSessionId();
            
            const headers = {
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true',
                ...options.headers,
            };
            
            // Add session_id as Bearer token if exists
            if (sessionId) {
                headers['Authorization'] = `Bearer ${sessionId}`;
            }
            
            const url = `${API_BASE_URL}${endpoint}`;
            
            console.log('🌐 API Request:', {
                url: url,
                method: options.method || 'GET',
                headers: headers,
                body: options.body
            });
            
            try {
                const response = await fetch(url, {
                    ...options,
                    headers,
                });
                
                console.log('📡 Response Status:', response.status, response.statusText);
                
                // Try to parse JSON response
                let data;
                const contentType = response.headers.get('content-type');
                
                if (contentType && contentType.includes('application/json')) {
                    data = await response.json();
                } else {
                    // If not JSON, get text
                    const text = await response.text();
                    data = { message: text };
                }
                
                console.log('📦 Response Data:', data);
                
                // Handle 401 Unauthorized - session expired
                if (response.status === 401 && endpoint !== '/v1/auth/login') {
                    console.log('🔒 Session expired, logging out...');
                    Auth.logout();
                    location.reload();
                    return;
                }
                
                if (!response.ok) {
                    // Extract error message from various possible formats
                    const errorMessage = data.detail || data.message || data.error || JSON.stringify(data) || 'Request failed';
                    console.error('❌ API Error:', errorMessage);
                    throw new Error(errorMessage);
                }
                
                return data;
            } catch (error) {
                console.error('💥 Fetch Error:', error);
                // If it's already an Error with a message, throw it
                if (error instanceof Error) {
                    throw error;
                }
                // Otherwise, convert to string
                throw new Error(String(error));
            }
        }

        // ============================================
        // AUTH HANDLERS
        // ============================================
        async function handleLogin(event) {
            event.preventDefault();
            
            const form = event.target;
            const email = form.querySelector('input[type="email"]').value;
            const password = document.getElementById('loginPassword').value;
            const submitBtn = form.querySelector('.btn-submit');
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Logging in...';
            
            try {
                // Send login request to /auth/login
                const response = await apiRequest('/v1/auth/login', {
                    method: 'POST',
                    body: JSON.stringify({ 
                        email: email, 
                        password: password 
                    }),
                });
                
                console.log('✅ Login response:', response);
                
                // Save session_id from response
                if (response.session_id) {
                    Auth.setSessionId(response.session_id);
                    console.log('✅ Session ID saved:', response.session_id);
                }
                
                // Save user info (just email for now - static "User" display)
                Auth.setUser({ email: email });
                
                // Update UI
                updateUIForLoggedInUser();
                closeLoginModalFunc();
                
            } catch (error) {
                console.error('Login error:', error);
                
                // Display user-friendly error message
                let errorMessage = 'Login failed. Please try again.';
                
                if (error.message) {
                    errorMessage = error.message;
                } else if (typeof error === 'string') {
                    errorMessage = error;
                }
                
                showToast(errorMessage, 'error', 'Login Failed');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Login';
            }
        }

        async function handleSignup(event) {
            event.preventDefault();
            
            const form = event.target;
            const username = form.querySelector('input[type="text"]').value;
            const email = form.querySelector('input[type="email"]').value;
            const password = document.getElementById('signupPassword').value;
            const submitBtn = form.querySelector('.btn-submit');
            
            // Log what we're sending
            const requestData = {
                email: email,
                password: password,
                username: username
            };
            
            console.log('📤 Sending signup request:', requestData);
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating account...';
            
            try {
                // Send signup request to /auth/signup
                const response = await apiRequest('/v1/auth/signup', {
                    method: 'POST',
                    body: JSON.stringify(requestData),
                });
                
                console.log('✅ Signup response:', response);
                
                // Close signup modal
                closeSignupModalFunc();
                
                // Show email verification message
                showEmailVerificationMessage(email);
                
            } catch (error) {
                console.error('❌ Signup error:', error);
                
                // Display user-friendly error message
                let errorMessage = 'Signup failed. Please try again.';
                
                if (error.message) {
                    errorMessage = error.message;
                } else if (typeof error === 'string') {
                    errorMessage = error;
                }
                
                showToast(errorMessage, 'error', 'Signup Failed');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Sign Up';
            }
        }

        function handleLogout() {
            // Show logout confirmation modal
            openLogoutModal();
        }

        function openLogoutModal() {
            const modal = document.getElementById('logoutModal');
            modal.classList.add('active');
            document.body.classList.add('modal-open');
        }

        function closeLogoutModal() {
            const modal = document.getElementById('logoutModal');
            modal.classList.remove('active');
            document.body.classList.remove('modal-open');
        }

        async function confirmLogout() {
            closeLogoutModal();
            
            try {
                const sessionId = Auth.getSessionId();
                
                if (sessionId) {
                    // Call logout API with session_id
                    await apiRequest('/v1/auth/logout', {
                        method: 'POST',
                        body: JSON.stringify({ 
                            session_id: sessionId 
                        }),
                    });
                }
            } catch (error) {
                console.error('Logout API error:', error);
                // Continue with logout even if API fails
            } finally {
                // Clear all data and reload
                Auth.logout();
                location.reload();
            }
        }

        // ============================================
        // TOKEN REFRESH
        // ============================================
        async function refreshAccessToken() {
            try {
                const refreshToken = Auth.getRefreshToken();
                
                if (!refreshToken) {
                    throw new Error('No refresh token available');
                }
                
                const response = await apiRequest('/v1/auth/refresh', {
                    method: 'POST',
                    body: JSON.stringify({ 
                        refresh_token: refreshToken 
                    }),
                });
                
                // Save new tokens
                Auth.setToken(response.access_token || response.token);
                if (response.refresh_token) {
                    Auth.setRefreshToken(response.refresh_token);
                }
                
                return response.access_token || response.token;
            } catch (error) {
                console.error('Token refresh failed:', error);
                // If refresh fails, logout user
                Auth.logout();
                location.reload();
                throw error;
            }
        }

        // ============================================
        // FORGOT PASSWORD
        // ============================================
        async function handleForgotPassword(event) {
            event.preventDefault();
            
            const email = document.getElementById('resetEmail').value;
            const submitBtn = event.target.querySelector('.btn-submit');
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';
            
            try {
                await apiRequest('/v1/auth/password-reset/request', {
                    method: 'POST',
                    body: JSON.stringify({ email }),
                });
                
                // Close modal
                closeForgotPasswordModal();
                
                // Show success message
                showToast('If the account you entered is correct, you will have received a message on it.', 'info', 'Check Your Email');
                
            } catch (error) {
                // Even on error, show the same message for security
                closeForgotPasswordModal();
                showToast('If the account you entered is correct, you will have received a message on it.', 'info', 'Check Your Email');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send Reset Link';
            }
        }

        function openForgotPasswordModal() {
            const modal = document.getElementById('forgotPasswordModal');
            modal.classList.add('active');
            document.body.classList.add('modal-open');
        }

        function closeForgotPasswordModal() {
            const modal = document.getElementById('forgotPasswordModal');
            modal.classList.remove('active');
            document.body.classList.remove('modal-open');
            document.getElementById('resetEmail').value = '';
        }

        // ============================================
        // EMAIL VERIFICATION
        // ============================================
        function showEmailVerificationMessage(email) {
            const modal = document.createElement('div');
            modal.className = 'modal-overlay active';
            modal.innerHTML = `
                <div class="modal-content" style="text-align: center; max-width: 500px;">
                    <button class="modal-close" onclick="this.parentElement.parentElement.remove(); document.body.classList.remove('modal-open'); document.querySelector('.hamburger-menu').classList.remove('blur'); document.querySelector('.container').classList.remove('blur'); document.querySelector('.sidebar').classList.remove('blur');">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                    
                    <div style="margin-bottom: 25px;">
                        <svg width="80" height="80" viewBox="0 0 24 24" fill="none" style="margin: 0 auto;">
                            <circle cx="12" cy="12" r="10" stroke="url(#grad1)" stroke-width="2"/>
                            <path d="M12 8v4M12 16h.01" stroke="url(#grad1)" stroke-width="2" stroke-linecap="round"/>
                            <defs>
                                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:#71038F;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#0033FF;stop-opacity:1" />
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                    
                    <h2 style="font-size: 28px; font-weight: 700; background: linear-gradient(135deg, #71038F 0%, #0033FF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 15px;">
                        Verify Your Email
                    </h2>
                    
                    <p style="font-size: 15px; color: #666; margin-bottom: 25px; line-height: 1.6;">
                        We've sent a verification link to<br>
                        <strong style="color: #333;">${email}</strong>
                    </p>
                    
                    <p style="font-size: 14px; color: #999; margin-bottom: 30px;">
                        Please check your email and click the verification link to activate your account.
                    </p>
                    
                    <button onclick="this.parentElement.parentElement.remove(); document.body.classList.remove('modal-open'); document.querySelector('.hamburger-menu').classList.remove('blur'); document.querySelector('.container').classList.remove('blur'); document.querySelector('.sidebar').classList.remove('blur');" style="
                        width: 100%;
                        padding: 13px;
                        background: linear-gradient(135deg, #71038F 0%, #0033FF 100%);
                        color: white;
                        border: none;
                        border-radius: 10px;
                        font-size: 15px;
                        font-weight: 600;
                        cursor: pointer;
                        font-family: 'Poppins', sans-serif;
                        transition: all 0.3s ease;
                    ">
                        Got it!
                    </button>
                    
                    <p style="font-size: 13px; color: #999; margin-top: 20px;">
                        Didn't receive the email? Check your spam folder or 
                        <a href="#" onclick="resendVerificationEmail('${email}'); return false;" style="color: #71038F; text-decoration: none; font-weight: 600;">resend verification email</a>
                    </p>
                </div>
            `;
            document.body.appendChild(modal);
            document.body.classList.add('modal-open');
            document.querySelector('.hamburger-menu').classList.add('blur');
            document.querySelector('.container').classList.add('blur');
            document.querySelector('.sidebar').classList.add('blur');
        }

        async function resendVerificationEmail(email) {
            try {
                await apiRequest('/v1/auth/resend-verification', {
                    method: 'POST',
                    body: JSON.stringify({ email }),
                });
                showToast('Verification email sent! Please check your inbox.', 'success', 'Email Sent');
            } catch (error) {
                showToast(error.message || 'Failed to resend email. Please try again.', 'error', 'Failed');
            }
        }

        // ============================================
        // EMAIL VERIFICATION HANDLER (when user clicks link)
        // ============================================
        async function handleEmailVerification() {
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('verify_token') || urlParams.get('token');
            
            if (token) {
                try {
                    // Show loading
                    const loadingDiv = document.createElement('div');
                    loadingDiv.style.cssText = 'position: fixed; inset: 0; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 9999;';
                    loadingDiv.innerHTML = '<div style="text-align: center; color: white;"><div style="font-size: 24px; margin-bottom: 10px;">⏳</div><div>Verifying your email...</div></div>';
                    document.body.appendChild(loadingDiv);
                    
                    // Verify email with backend
                    const response = await apiRequest('/v1/auth/verify-email', {
                        method: 'POST',
                        body: JSON.stringify({ token }),
                    });
                    
                    // Remove loading
                    loadingDiv.remove();
                    
                    // Save tokens and get user info
                    Auth.setToken(response.access_token || response.token);
                    if (response.refresh_token) {
                        Auth.setRefreshToken(response.refresh_token);
                    }
                    
                    const userInfo = await apiRequest('/v1/users/me', {
                        method: 'GET',
                    });
                    
                    Auth.setUser(userInfo);
                    updateUIForLoggedInUser();
                    
                    // Clean URL
                    window.history.replaceState({}, document.title, window.location.pathname);
                    
                    // Show success message
                    showToast('Email verified successfully! Welcome to ScholarMind!', 'success', 'Verification Complete');
                    
                } catch (error) {
                    showToast('Email verification failed. The link may be expired or invalid.', 'error', 'Verification Failed');
                    // Clean URL even on error
                    window.history.replaceState({}, document.title, window.location.pathname);
                }
            }
        }

        // ============================================
        // UI UPDATES
        // ============================================
        function updateUIForLoggedInUser() {
            const user = Auth.getUser();
            const authButtons = document.querySelector('.auth-buttons');
            const mainHeading = document.getElementById('mainHeading');
            
            if (authButtons && user) {
                authButtons.innerHTML = `
                    <span style="margin-right: 15px; color: #333; font-weight: 500;">Welcome, User</span>
                `;
            }
            
            // Update main heading to show static "User"
            if (mainHeading && user) {
                mainHeading.textContent = '';
                mainHeading.appendChild(document.createTextNode('Welcome, User!'));
                mainHeading.appendChild(document.createElement('br'));
                mainHeading.appendChild(document.createTextNode('What are you researching today?'));
            }
            
            // Update sidebar profile with static "User"
            const profileName = document.querySelector('.profile-name');
            const profileEmail = document.querySelector('.profile-email');
            
            if (profileName && user) {
                profileName.textContent = 'User';
            }
            
            if (profileEmail && user) {
                profileEmail.textContent = user.email || '';
            }
        }

        function checkAuthBeforeAction(actionName) {
            if (!Auth.isLoggedIn()) {
                openLoginModal();
                return false;
            }
            return true;
        }

        // ============================================
        // DOM ELEMENTS & EVENT HANDLERS
        // ============================================
        // Get elements
        const hamburgerBtn = document.getElementById('hamburgerBtn');
        const sidebar = document.getElementById('sidebar');
        const closeBtn = document.getElementById('closeBtn');
        const container = document.querySelector('.container');
        const sidebarOverlay = document.getElementById('sidebarOverlay');

        // Modal elements
        const loginModal = document.getElementById('loginModal');
        const signupModal = document.getElementById('signupModal');
        const forgotPasswordModal = document.getElementById('forgotPasswordModal');
        const logoutModal = document.getElementById('logoutModal');
        const btnLogin = document.querySelector('.btn-login');
        const btnSignup = document.querySelector('.btn-signup');
        const closeLoginModal = document.getElementById('closeLoginModal');
        const closeSignupModal = document.getElementById('closeSignupModal');
        const closeForgotPasswordModalBtn = document.getElementById('closeForgotPasswordModal');
        const switchToSignup = document.getElementById('switchToSignup');
        const switchToLogin = document.getElementById('switchToLogin');
        const forgotPasswordLink = document.querySelector('.forgot-password a');
        const cancelLogoutBtn = document.getElementById('cancelLogout');
        const confirmLogoutBtn = document.getElementById('confirmLogout');

        // Function to open sidebar
        function openSidebar() {
            sidebar.classList.add('active');
            container.classList.add('sidebar-open');
            hamburgerBtn.classList.add('sidebar-open');
            sidebarOverlay.classList.add('active');
        }

        // Function to close sidebar
        function closeSidebar() {
            sidebar.classList.remove('active');
            container.classList.remove('sidebar-open');
            hamburgerBtn.classList.remove('sidebar-open');
            sidebarOverlay.classList.remove('active');
        }

        // Function to open login modal
        function openLoginModal() {
            loginModal.classList.add('active');
            document.body.classList.add('modal-open');
        }

        // Function to close login modal
        function closeLoginModalFunc() {
            loginModal.classList.remove('active');
            document.body.classList.remove('modal-open');
        }

        // Function to open signup modal
        function openSignupModal() {
            signupModal.classList.add('active');
            document.body.classList.add('modal-open');
        }

        // Function to close signup modal
        function closeSignupModalFunc() {
            signupModal.classList.remove('active');
            document.body.classList.remove('modal-open');
        }

        // Sidebar event listeners
        hamburgerBtn.addEventListener('click', function() {
            // Check if user is logged in
            if (!Auth.isLoggedIn()) {
                openLoginModal();
                return;
            }
            
            if (sidebar.classList.contains('active')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
        
        closeBtn.addEventListener('click', closeSidebar);

        // Close sidebar when clicking on overlay
        sidebarOverlay.addEventListener('click', closeSidebar);

        // Login modal event listeners
        btnLogin.addEventListener('click', openLoginModal);
        closeLoginModal.addEventListener('click', closeLoginModalFunc);

        // Signup modal event listeners
        btnSignup.addEventListener('click', openSignupModal);
        closeSignupModal.addEventListener('click', closeSignupModalFunc);

        // Forgot password modal event listeners
        if (forgotPasswordLink) {
            forgotPasswordLink.addEventListener('click', function(e) {
                e.preventDefault();
                closeLoginModalFunc();
                setTimeout(openForgotPasswordModal, 300);
            });
        }
        
        if (closeForgotPasswordModalBtn) {
            closeForgotPasswordModalBtn.addEventListener('click', closeForgotPasswordModal);
        }

        // Logout modal event listeners
        if (cancelLogoutBtn) {
            cancelLogoutBtn.addEventListener('click', closeLogoutModal);
        }

        if (confirmLogoutBtn) {
            confirmLogoutBtn.addEventListener('click', confirmLogout);
        }

        // Switch between modals
        switchToSignup.addEventListener('click', function(e) {
            e.preventDefault();
            closeLoginModalFunc();
            setTimeout(openSignupModal, 300);
        });

        switchToLogin.addEventListener('click', function(e) {
            e.preventDefault();
            closeSignupModalFunc();
            setTimeout(openLoginModal, 300);
        });

        // Close modals when clicking outside
        loginModal.addEventListener('click', function(e) {
            if (e.target === loginModal) {
                closeLoginModalFunc();
            }
        });

        signupModal.addEventListener('click', function(e) {
            if (e.target === signupModal) {
                closeSignupModalFunc();
            }
        });

        forgotPasswordModal.addEventListener('click', function(e) {
            if (e.target === forgotPasswordModal) {
                closeForgotPasswordModal();
            }
        });

        logoutModal.addEventListener('click', function(e) {
            if (e.target === logoutModal) {
                closeLogoutModal();
            }
        });

        // Close sidebar and modals when pressing Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeSidebar();
                closeLoginModalFunc();
                closeSignupModalFunc();
                closeForgotPasswordModal();
                closeLogoutModal();
            }
        });

        // ============================================
        // SEARCH BUTTON - CHECK AUTH
        // ============================================
        const searchBtn = document.querySelector('.search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (!checkAuthBeforeAction('search for research papers')) {
                    return;
                }
                // Continue with search functionality
                const searchInput = document.querySelector('.search-box');
                const query = searchInput.value.trim();
                if (query) {
                    console.log('Searching for:', query);
                    // Add your search logic here
                } else {
                    showToast('Please enter a search query', 'warning', 'Search Required');
                }
            });
        }

        // ============================================
        // UPLOAD BUTTON - CHECK AUTH
        // ============================================
        const uploadSection = document.querySelector('.upload-section');
        if (uploadSection) {
            uploadSection.addEventListener('click', function(e) {
                e.preventDefault();
                if (!checkAuthBeforeAction('upload papers')) {
                    return;
                }
                // Continue with upload functionality
                console.log('Upload clicked');
                // Add your upload logic here
            });
        }

        // ============================================
        // SIDEBAR LOGOUT BUTTON
        // ============================================
        const sidebarLogoutBtn = document.getElementById('sidebarLogoutBtn');
        if (sidebarLogoutBtn) {
            sidebarLogoutBtn.addEventListener('click', handleLogout);
        }

        // ============================================
        // FORM SUBMISSIONS
        // ============================================
        // Handle login form submission
        document.querySelector('#loginModal form').addEventListener('submit', handleLogin);
        
        // Handle signup form submission
        document.querySelector('#signupModal form').addEventListener('submit', handleSignup);
        
        // Handle forgot password form submission
        document.querySelector('#forgotPasswordForm').addEventListener('submit', handleForgotPassword);

        // ============================================
        // INITIALIZE ON PAGE LOAD
        // ============================================
        document.addEventListener('DOMContentLoaded', function() {
            // Check for email verification token in URL
            handleEmailVerification();
            
            // Check if user is already logged in
            if (Auth.isLoggedIn()) {
                updateUIForLoggedInUser();
            }
        });