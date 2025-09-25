import React, { useState } from "react";
import ChatWidget from "../components/ChatbotWidget/ChatWidget";
import PricingModal from "./PricingModal";
import BookingModal from "./BookingModal";
import {
  Menu,
  X,
  Code,
  Smartphone,
  Zap,
  Search,
  Share2,
  Palette,
  ChevronDown,
  Phone,
  Mail,
  MapPin,
  Star,
  CheckCircle,
  ArrowRight,
  Globe,
  Users,
  Award,
  Loader2,
} from "lucide-react";

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isPricingModalOpen, setIsPricingModalOpen] = useState(false);
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);
  const [contactForm, setContactForm] = useState({
    name: "",
    email: "",
    message: "",
  });
  const [contactLoading, setContactLoading] = useState(false);
  const [contactSubmitted, setContactSubmitted] = useState(false);
  const [logoError, setLogoError] = useState(false);

  const services = [
    {
      icon: <Code className="w-8 h-8" />,
      title: "Web Development",
      description:
        "Custom responsive websites and web applications built with modern technologies",
      features: [
        "React/Vue.js",
        "Node.js",
        "Database Integration",
        "API Development",
      ],
    },
    {
      icon: <Smartphone className="w-8 h-8" />,
      title: "Mobile Apps",
      description:
        "Native and cross-platform mobile applications for iOS and Android",
      features: [
        "React Native",
        "Flutter",
        "Native iOS/Android",
        "App Store Deployment",
      ],
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Web3 & Blockchain",
      description: "Decentralized applications and blockchain solutions",
      features: [
        "Smart Contracts",
        "DeFi Solutions",
        "NFT Platforms",
        "Crypto Wallets",
      ],
    },
    {
      icon: <Search className="w-8 h-8" />,
      title: "SEO Optimization",
      description: "Boost your online visibility and organic search rankings",
      features: [
        "Keyword Research",
        "On-page SEO",
        "Technical SEO",
        "Local SEO",
      ],
    },
    {
      icon: <Share2 className="w-8 h-8" />,
      title: "Social Media Marketing",
      description: "Grow your brand presence and engage with your audience",
      features: [
        "Content Strategy",
        "Social Media Management",
        "Paid Advertising",
        "Analytics",
      ],
    },
    {
      icon: <Palette className="w-8 h-8" />,
      title: "Graphic Design",
      description: "Professional branding and marketing materials",
      features: [
        "Logo Design",
        "Brand Identity",
        "Marketing Materials",
        "UI/UX Design",
      ],
    },
  ];

  const projects = [
    { name: "Save Planet Earth", type: "Web3 Platform", status: "Completed" },
    { name: "Estate Slice", type: "Real Estate Platform", status: "Completed" },
    { name: "Kutee Kitty", type: "NFT Collection", status: "Completed" },
  ];

  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth" });
    setIsMenuOpen(false);
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setContactLoading(true);

    const apiBaseUrl =
      process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api";

    try {
      await fetch(`${apiBaseUrl}/upsert-hubspot`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: contactForm.name,
          email: contactForm.email,
          company: "",
          interest: "Contact Form",
          session_id: `contact_${Date.now()}_${Math.random()
            .toString(36)
            .substr(2, 9)}`,
        }),
      });

      setContactSubmitted(true);
      setContactForm({ name: "", email: "", message: "" });
    } catch (error) {
      console.error("Contact form error:", error);
      alert("There was an error sending your message. Please try again.");
    } finally {
      setContactLoading(false);
    }
  };

  const handleContactChange = (e) => {
    const { name, value } = e.target;
    setContactForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-metalogics-light via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/95 backdrop-blur-sm shadow-lg sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              {!logoError ? (
                <img
                  src="/assets/metalogics icon.png"
                  alt="Metalogics"
                  className="w-8 h-8"
                  onError={() => setLogoError(true)}
                />
              ) : (
                <div className="w-8 h-8 bg-gradient-to-r from-metalogics-primary to-metalogics-secondary rounded flex items-center justify-center">
                  <span className="text-white font-bold text-sm">M</span>
                </div>
              )}
              <span className="text-2xl font-bold bg-gradient-to-r from-metalogics-primary to-metalogics-secondary bg-clip-text text-transparent">
                Metalogics
              </span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <button
                onClick={() => scrollToSection("home")}
                className="text-gray-700 hover:text-metalogics-primary transition-colors"
              >
                Home
              </button>
              <button
                onClick={() => scrollToSection("services")}
                className="text-gray-700 hover:text-metalogics-primary transition-colors"
              >
                Services
              </button>
              <button
                onClick={() => scrollToSection("about")}
                className="text-gray-700 hover:text-metalogics-primary transition-colors"
              >
                About
              </button>
              <button
                onClick={() => scrollToSection("portfolio")}
                className="text-gray-700 hover:text-metalogics-primary transition-colors"
              >
                Portfolio
              </button>
              <button
                onClick={() => scrollToSection("contact")}
                className="text-gray-700 hover:text-metalogics-primary transition-colors"
              >
                Contact
              </button>
              <button
                onClick={() => scrollToSection("contact")}
                className="bg-gradient-to-r from-metalogics-primary to-metalogics-secondary text-white px-6 py-2 rounded-full hover:shadow-lg transition-all duration-300 transform hover:scale-105"
              >
                Get Started
              </button>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-md text-gray-700 hover:text-metalogics-primary"
            >
              {isMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>

          {/* Mobile Navigation */}
          {isMenuOpen && (
            <div className="md:hidden border-t border-gray-200 py-4">
              <div className="flex flex-col space-y-4">
                <button
                  onClick={() => scrollToSection("home")}
                  className="text-left text-gray-700 hover:text-metalogics-primary transition-colors"
                >
                  Home
                </button>
                <button
                  onClick={() => scrollToSection("services")}
                  className="text-left text-gray-700 hover:text-metalogics-primary transition-colors"
                >
                  Services
                </button>
                <button
                  onClick={() => scrollToSection("about")}
                  className="text-left text-gray-700 hover:text-metalogics-primary transition-colors"
                >
                  About
                </button>
                <button
                  onClick={() => scrollToSection("portfolio")}
                  className="text-left text-gray-700 hover:text-metalogics-primary transition-colors"
                >
                  Portfolio
                </button>
                <button
                  onClick={() => scrollToSection("contact")}
                  className="text-left text-gray-700 hover:text-metalogics-primary transition-colors"
                >
                  Contact
                </button>
                <button
                  onClick={() => scrollToSection("contact")}
                  className="text-left bg-gradient-to-r from-metalogics-primary to-metalogics-secondary text-white px-4 py-2 rounded-full hover:shadow-lg transition-all duration-300"
                >
                  Get Started
                </button>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6">
              Innovative
              <span className="bg-gradient-to-r from-metalogics-primary to-metalogics-secondary bg-clip-text text-transparent">
                {" "}
                Technology{" "}
              </span>
              Solutions
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Transform your business with cutting-edge web development, mobile
              apps, and Web3 solutions. Trusted by 300+ clients worldwide.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => scrollToSection("services")}
                className="bg-gradient-to-r from-metalogics-primary to-metalogics-secondary text-white px-8 py-4 rounded-full text-lg font-semibold hover:shadow-xl transition-all duration-300 transform hover:scale-105"
              >
                Explore Services
              </button>
              <button
                onClick={() => setIsPricingModalOpen(true)}
                className="border-2 border-metalogics-primary text-metalogics-primary px-8 py-4 rounded-full text-lg font-semibold hover:bg-metalogics-primary hover:text-white transition-all duration-300"
              >
                View Pricing
              </button>
              <button
                onClick={() => setIsBookingModalOpen(true)}
                className="bg-white text-metalogics-primary px-8 py-4 rounded-full text-lg font-semibold hover:shadow-xl transition-all duration-300 transform hover:scale-105"
              >
                Book a Demo
              </button>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="bg-white/50 backdrop-blur-sm py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-3xl font-bold text-metalogics-primary">
                  300+
                </div>
                <div className="text-gray-600">Happy Clients</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-metalogics-primary">
                  500+
                </div>
                <div className="text-gray-600">Projects Completed</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-metalogics-primary">
                  50+
                </div>
                <div className="text-gray-600">Web3 Projects</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-metalogics-primary">
                  4+
                </div>
                <div className="text-gray-600">Years Experience</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Our Services
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              From traditional web development to cutting-edge Web3 solutions,
              we deliver comprehensive digital services.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {services.map((service, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-white to-gray-50 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2"
              >
                <div className="text-metalogics-primary mb-4">
                  {service.icon}
                </div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                  {service.title}
                </h3>
                <p className="text-gray-600 mb-4">{service.description}</p>
                <ul className="space-y-2">
                  {service.features.map((feature, idx) => (
                    <li
                      key={idx}
                      className="flex items-center text-sm text-gray-700"
                    >
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section
        id="about"
        className="py-24 bg-gradient-to-r from-metalogics-primary/5 to-metalogics-secondary/5"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                About Metalogics
              </h2>
              <p className="text-lg text-gray-600 mb-6">
                Founded in 2020, Metalogics is a UK-based digital agency
                specializing in web development, mobile applications, and
                Web3/blockchain solutions. We're passionate about helping
                businesses leverage technology to achieve their goals.
              </p>
              <div className="space-y-4">
                <div className="flex items-center">
                  <Award className="w-6 h-6 text-metalogics-primary mr-3" />
                  <span className="text-gray-700">
                    Trusted by 300+ clients worldwide
                  </span>
                </div>
                <div className="flex items-center">
                  <Users className="w-6 h-6 text-metalogics-primary mr-3" />
                  <span className="text-gray-700">
                    500+ successful projects delivered
                  </span>
                </div>
                <div className="flex items-center">
                  <Globe className="w-6 h-6 text-metalogics-primary mr-3" />
                  <span className="text-gray-700">
                    Based in Slough, Berkshire, UK
                  </span>
                </div>
              </div>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-lg">
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                Why Choose Us?
              </h3>
              <div className="space-y-4">
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <div>
                    <div className="font-semibold text-gray-900">
                      Fast Turnaround
                    </div>
                    <div className="text-gray-600">
                      24-48 hour delivery for most updates
                    </div>
                  </div>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <div>
                    <div className="font-semibold text-gray-900">
                      Budget-Friendly
                    </div>
                    <div className="text-gray-600">
                      Transparent pricing with no hidden costs
                    </div>
                  </div>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <div>
                    <div className="font-semibold text-gray-900">
                      One-Stop Shop
                    </div>
                    <div className="text-gray-600">
                      Web2 + Web3 solutions under one roof
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Portfolio Section */}
      <section id="portfolio" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Our Portfolio
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Showcasing our successful projects and satisfied clients.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {projects.map((project, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-gray-50 to-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-gray-900">
                    {project.name}
                  </h3>
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                    {project.status}
                  </span>
                </div>
                <p className="text-gray-600 mb-4">{project.type}</p>
                <div className="flex items-center">
                  <div className="flex text-yellow-400">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-current" />
                    ))}
                  </div>
                  <span className="text-gray-600 ml-2 text-sm">
                    Client Satisfaction
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section
        id="contact"
        className="py-24 bg-gradient-to-r from-metalogics-primary to-metalogics-secondary"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              Get Started Today
            </h2>
            <p className="text-xl text-white/90 max-w-2xl mx-auto">
              Ready to transform your business? Let's discuss your project and
              create something amazing together.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12">
            <div className="bg-white/10 backdrop-blur-sm p-8 rounded-2xl">
              <h3 className="text-2xl font-semibold text-white mb-6">
                Contact Information
              </h3>
              <div className="space-y-4">
                <div className="flex items-center text-white">
                  <Mail className="w-6 h-6 mr-3" />
                  <span>hello@metalogics.io</span>
                </div>
                <div className="flex items-center text-white">
                  <Phone className="w-6 h-6 mr-3" />
                  <span>+44 7368 580133</span>
                </div>
                <div className="flex items-center text-white">
                  <MapPin className="w-6 h-6 mr-3" />
                  <span>Slough, Berkshire, United Kingdom</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-lg">
              <h3 className="text-2xl font-semibold text-gray-900 mb-6">
                Send us a Message
              </h3>
              {contactSubmitted ? (
                <div className="text-center py-8">
                  <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">
                    Message Sent!
                  </h4>
                  <p className="text-gray-600">
                    We'll get back to you within 24 hours.
                  </p>
                </div>
              ) : (
                <form onSubmit={handleContactSubmit} className="space-y-4">
                  <div>
                    <input
                      type="text"
                      name="name"
                      value={contactForm.name}
                      onChange={handleContactChange}
                      placeholder="Your Name"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-metalogics-primary"
                      required
                    />
                  </div>
                  <div>
                    <input
                      type="email"
                      name="email"
                      value={contactForm.email}
                      onChange={handleContactChange}
                      placeholder="Your Email"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-metalogics-primary"
                      required
                    />
                  </div>
                  <div>
                    <textarea
                      rows="4"
                      name="message"
                      value={contactForm.message}
                      onChange={handleContactChange}
                      placeholder="Tell us about your project"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-metalogics-primary"
                    ></textarea>
                  </div>
                  <button
                    type="submit"
                    disabled={contactLoading}
                    className="w-full bg-gradient-to-r from-metalogics-primary to-metalogics-secondary text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {contactLoading ? "Sending..." : "Send Message"}
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                {!logoError ? (
                  <img
                    src="/assets/metalogics icon.png"
                    alt="Metalogics"
                    className="w-8 h-8"
                    onError={() => setLogoError(true)}
                  />
                ) : (
                  <div className="w-8 h-8 bg-gradient-to-r from-metalogics-primary to-metalogics-secondary rounded flex items-center justify-center">
                    <span className="text-white font-bold text-sm">M</span>
                  </div>
                )}
                <span className="text-2xl font-bold">Metalogics</span>
              </div>
              <p className="text-gray-400">
                Innovative technology solutions for modern businesses.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Services</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Web Development</li>
                <li>Mobile Apps</li>
                <li>Web3 & Blockchain</li>
                <li>SEO Optimization</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li>About Us</li>
                <li>Portfolio</li>
                <li>Contact</li>
                <li>Careers</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Connect</h4>
              <ul className="space-y-2 text-gray-400">
                <li>hello@metalogics.io</li>
                <li>+44 7368 580133</li>
                <li>metalogics.io</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Metalogics. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Chat Widget */}
      <ChatWidget baseApiUrl="http://localhost:8000" onBookDemo={() => setIsBookingModalOpen(true)} />

      {/* Pricing Modal */}
      <PricingModal
        isOpen={isPricingModalOpen}
        onClose={() => setIsPricingModalOpen(false)}
      />

      {/* Booking Modal */}
      <BookingModal
        isOpen={isBookingModalOpen}
        onClose={() => setIsBookingModalOpen(false)}
      />
    </div>
  );
}

export default App;
