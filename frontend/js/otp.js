async function verifyOTP() {
    const otp = document.querySelector(".otp-input").value;
    const urlParams = new URLSearchParams(window.location.search);
    const email = urlParams.get("email");

    if (!otp) {
        alert("Enter OTP");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/auth/verify-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, otp })
        });

        const data = await res.json();

        if (res.status === 200) {
            alert("Email verified successfully!");
            window.location.href = "login.html";
        } else {
            alert(data.message || "Verification failed");
        }

    } catch (err) {
        alert("Server error");
        console.log(err);
    }
}
