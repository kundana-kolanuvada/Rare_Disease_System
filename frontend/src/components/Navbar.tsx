import { Link } from "react-router-dom";
import "./Navbar.css";

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="logo">
        <img src="/logo.png" alt="AtlasDx Logo" />
      </div>

      <div className="nav-links">
        <Link to="/">Home</Link>
        <Link to="/diagnose">Diagnose</Link>
        <Link to="/about">About</Link>
      </div>
    </nav>
  );
};

export default Navbar;
