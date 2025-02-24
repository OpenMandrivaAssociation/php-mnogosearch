%define modname mnogosearch
%define dirname %{modname}
%define soname %{modname}.so
%define inifile 34_%{modname}.ini

Summary:	MnoGoSearch extension module for PHP
Name:		php-%{modname}
Version:	1.96
Release:	%mkrel 37
Group:		Development/PHP
URL:		https://www.mnogosearch.org/
License:	PHP License
Source0:	%{modname}-php-extension-%{version}.tar.bz2
Patch0:		php-mnogosearch-build_fix.diff
Patch1:		mnogosearch-php-extension-1.96-php54x.diff
BuildRequires:	php-devel >= 3:5.2.0
BuildRequires:	libmnogosearch-devel >= 3.2.20
BuildRequires:	postgresql-devel
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
This is a dynamic shared object (DSO) for PHP that will allow you to access
mnoGoSearch free search engine.

%prep

%setup -q -n %{version}
%patch0 -p0
%patch1 -p0

MnoGoSearchVersion=`%{_bindir}/mnogosearch-*-config --version`

# hack :)
perl -p -i -e "s|udm-config|mnogosearch-${MnoGoSearchVersion}-config|g" config.m4

%build
%serverbuild

MnoGoSearchVersion=`%{_bindir}/mnogosearch-*-config --version`
export EXTRA_INCLUDES="-I%{_includedir}/mnogosearch-${MnoGoSearchVersion} -I%{_includedir} -I%{_includedir}/pgsql"

phpize
%configure2_5x --with-libdir=%{_lib} \
    --with-%{modname}=shared,%{_prefix} \
    --with-openssl=%{_prefix}

%make
mv modules/*.so .
chrpath -d %{soname}

%install
rm -rf %{buildroot} 

install -d %{buildroot}%{_libdir}/php/extensions
install -d %{buildroot}%{_sysconfdir}/php.d

install -m755 %{soname} %{buildroot}%{_libdir}/php/extensions/

cat > %{buildroot}%{_sysconfdir}/php.d/%{inifile} << EOF
extension = %{soname}
EOF

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart >/dev/null || :
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart >/dev/null || :
    fi
fi

%clean
rm -rf %{buildroot}

%files 
%defattr(-,root,root)
%doc CREDITS README index.php
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/php.d/%{inifile}
%attr(0755,root,root) %{_libdir}/php/extensions/%{soname}
