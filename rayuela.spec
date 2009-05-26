%define py_version %(python -c "import sys; v=sys.version_info[:2]; print '%%d.%%d'%%v" 2>/dev/null || echo PYTHON-NOT-FOUND)
%define py_prefix  %(python -c "import sys; print sys.prefix" 2>/dev/null || echo PYTHON-NOT-FOUND)
%define py_libdir  %{py_prefix}/lib/python%{py_version}
%define py_incdir  %{py_prefix}/include/python%{py_version}
%define py_sitedir %{py_libdir}/site-packages

%define name rayuela
%define version 0.2
%define release 1

Summary: A fiction writing editor.
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
License: GNU
Group: Office
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Manuel Ospina <ospina.manuel@gmail.com>

%description
Rayuela is a fiction writing editor. It has basic editing features and keep
track of characters and locations.

%prep
%setup

%build

%install
python setup.py install --prefix=$RPM_BUILD_ROOT/usr

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{py_sitedir}
%{_bindir}/*
%{_datadir}/*
