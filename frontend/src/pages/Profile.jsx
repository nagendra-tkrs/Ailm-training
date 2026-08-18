import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getProfile,
  updateProfile,
  changePassword,
} from "../services/profileService";
import "./Profile.css";

function Profile() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [saveError, setSaveError] = useState("");

  const [profileForm, setProfileForm] = useState({
    name: "",
    email: "",
    phone_number: "",
    address: "",
  });

  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
  });
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState("");
  const [passwordError, setPasswordError] = useState("");

  const token = localStorage.getItem("token");

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getProfile(token);

      setProfile(data);
      setProfileForm({
        name: data.name || "",
        email: data.email || "",
        phone_number: data.phone_number || "",
        address: data.address || "",
      });
    } catch (error) {
      console.error("Profile error:", error);

      if (error.message === "AUTHENTICATION_ERROR") {
        localStorage.removeItem("token");
        navigate("/login");
        return;
      }

      setError("Unable to load profile.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!token) {
      localStorage.removeItem("token");
      navigate("/login");
      return;
    }

    fetchProfile();
  }, [token]);

  const handleSaveProfile = async (e) => {
    e.preventDefault();

    setMessage("");
    setSaveError("");

    if (!profileForm.name.trim()) {
      setSaveError("Name cannot be empty.");
      return;
    }

    if (!profileForm.email.trim()) {
      setSaveError("Email cannot be empty.");
      return;
    }

    const phone = profileForm.phone_number.trim();

    if (phone) {
      const digitsOnly = phone.replace(/[^0-9]/g, "");

      if (digitsOnly.length > 13) {
        setSaveError(
          "Phone number cannot have more than 10 digits. Format: country code + 10 digits, e.g. +919876543210."
        );
        return;
      }

      if (!/^\+[1-9]\d{1,3}\d{10}$/.test(phone)) {
        setSaveError(
          "Phone number must include a country code and exactly 10 digits, for example +919876543210."
        );
        return;
      }
    }

    try {
      setSaving(true);

      const updated = await updateProfile(token, {
        name: profileForm.name.trim(),
        email: profileForm.email.trim(),
        address: profileForm.address.trim() || null,
        phone_number: profileForm.phone_number.trim() || null,
      });

      setProfile(updated);
      setEditing(false);
      setMessage("Profile updated successfully.");
    } catch (error) {
      console.error("Update profile error:", error);

      if (error.message === "AUTHENTICATION_ERROR") {
        localStorage.removeItem("token");
        navigate("/login");
        return;
      }

      setSaveError(error.message || "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();

    setPasswordMessage("");
    setPasswordError("");

    if (!passwordForm.current_password) {
      setPasswordError("Please enter your current password.");
      return;
    }

    if (passwordForm.new_password.length < 8) {
      setPasswordError("New password must be at least 8 characters.");
      return;
    }

    try {
      setPasswordSaving(true);

      await changePassword(token, {
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      });

      setPasswordForm({
        current_password: "",
        new_password: "",
      });
      setPasswordMessage("Password changed successfully.");
    } catch (error) {
      console.error("Change password error:", error);

      if (error.message === "AUTHENTICATION_ERROR") {
        localStorage.removeItem("token");
        navigate("/login");
        return;
      }

      setPasswordError(error.message || "Failed to change password.");
    } finally {
      setPasswordSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-container">
          <div className="profile-loading">Loading profile...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-page">
        <div className="profile-container">
          <div className="profile-error">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-container">

        <div className="profile-header">
          <h1>My Profile</h1>
          <p>View and update your personal information</p>
        </div>

        <section className="profile-card">
          <div className="profile-head">
            <div className="profile-avatar">
              {profile && profile.name
                ? profile.name.charAt(0).toUpperCase()
                : "U"}
            </div>

            <div className="profile-head-info">
              <h2 className="profile-name">{profile ? profile.name : ""}</h2>
              <p className="profile-meta">
                {profile ? profile.role || "employee" : ""}
              </p>
            </div>

            <div className="profile-actions">
              {!editing && (
                <button
                  type="button"
                  className="profile-edit-button"
                  onClick={() => {
                    setEditing(true);
                    setMessage("");
                    setSaveError("");
                  }}
                >
                  Edit Profile
                </button>
              )}
            </div>
          </div>

          {message && <p className="success-message">{message}</p>}
          {saveError && <p className="form-error">{saveError}</p>}

          {editing ? (
            <form className="profile-form" onSubmit={handleSaveProfile}>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="profileName">Full Name</label>
                  <input
                    id="profileName"
                    type="text"
                    value={profileForm.name}
                    onChange={(e) =>
                      setProfileForm({ ...profileForm, name: e.target.value })
                    }
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="profileEmail">Email</label>
                  <input
                    id="profileEmail"
                    type="email"
                    value={profileForm.email}
                    onChange={(e) =>
                      setProfileForm({ ...profileForm, email: e.target.value })
                    }
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="profilePhone">Phone Number</label>
                  <input
                    id="profilePhone"
                    type="text"
                    placeholder="+919876543210"
                    maxLength="15"
                    value={profileForm.phone_number}
                    onChange={(e) =>
                      setProfileForm({
                        ...profileForm,
                        phone_number: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="profileAddress">Address</label>
                  <input
                    id="profileAddress"
                    type="text"
                    placeholder="Enter address"
                    value={profileForm.address}
                    onChange={(e) =>
                      setProfileForm({
                        ...profileForm,
                        address: e.target.value,
                      })
                    }
                  />
                </div>
              </div>

              <div className="profile-form-actions">
                <button type="submit" className="apply-leave-button" disabled={saving}>
                  {saving ? "Saving..." : "Save Profile"}
                </button>

                <button
                  type="button"
                  className="profile-cancel-button"
                  onClick={() => setEditing(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="profile-details">
              <div className="profile-detail">
                <span className="profile-detail-label">Employee ID</span>
                <span className="profile-detail-value">
                  {profile ? profile.employee_id || "-" : "-"}
                </span>
              </div>

              <div className="profile-detail">
                <span className="profile-detail-label">Name</span>
                <span className="profile-detail-value">
                  {profile ? profile.name || "-" : "-"}
                </span>
              </div>

              <div className="profile-detail">
                <span className="profile-detail-label">Role</span>
                <span className="profile-detail-value">
                  {profile ? profile.role || "-" : "-"}
                </span>
              </div>

              <div className="profile-detail">
                <span className="profile-detail-label">Email</span>
                <span className="profile-detail-value">
                  {profile ? profile.email || "-" : "-"}
                </span>
              </div>

              <div className="profile-detail">
                <span className="profile-detail-label">Phone</span>
                <span className="profile-detail-value">
                  {profile ? profile.phone_number || "-" : "-"}
                </span>
              </div>

              <div className="profile-detail">
                <span className="profile-detail-label">Address</span>
                <span className="profile-detail-value">
                  {profile ? profile.address || "-" : "-"}
                </span>
              </div>
            </div>
          )}

          <div className="profile-password">
            <h3>Change Password</h3>

            {passwordMessage && (
              <p className="success-message">{passwordMessage}</p>
            )}
            {passwordError && <p className="form-error">{passwordError}</p>}

            <form className="profile-form" onSubmit={handleChangePassword}>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="currentPassword">Current Password</label>
                  <input
                    id="currentPassword"
                    type="password"
                    placeholder="Enter current password"
                    value={passwordForm.current_password}
                    onChange={(e) =>
                      setPasswordForm({
                        ...passwordForm,
                        current_password: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="newPassword">New Password</label>
                  <input
                    id="newPassword"
                    type="password"
                    placeholder="At least 8 characters"
                    value={passwordForm.new_password}
                    onChange={(e) =>
                      setPasswordForm({
                        ...passwordForm,
                        new_password: e.target.value,
                      })
                    }
                  />
                </div>
              </div>

              <button
                type="submit"
                className="apply-leave-button password-button"
                disabled={passwordSaving}
              >
                {passwordSaving ? "Changing..." : "Change Password"}
              </button>
            </form>
          </div>
        </section>

      </div>
    </div>
  );
}

export default Profile;
