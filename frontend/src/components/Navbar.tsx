import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="text-2xl font-bold text-primary-600">
            Dropshipping
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex space-x-8">
            <Link to="/" className="text-gray-600 hover:text-primary-600">
              Home
            </Link>
            <Link to="/cart" className="text-gray-600 hover:text-primary-600">
              Cart
            </Link>
            <Link to="/orders" className="text-gray-600 hover:text-primary-600">
              Orders
            </Link>
          </div>

          {/* Auth Buttons */}
          <div className="flex space-x-4">
            <Link
              to="/login"
              className="btn btn-secondary"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="btn btn-primary"
            >
              Register
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 