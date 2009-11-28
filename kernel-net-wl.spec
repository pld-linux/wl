# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	verbose		# verbose build (V=1)

%define		_enable_debug_packages	0

%define		rel	0.2
%define		pname	wl
Summary:	Linux kernel module to BCM network cards
Name:		%{pname}%{_alt_kernel}
Version:	5.10.91.9.3
Release:	%{rel}
License:	other
Group:		Base/Kernel
Source0:	http://www.broadcom.com/docs/linux_sta/hybrid-portsrc-x86_32-v%{version}.tar.gz
# Source0-md5:	15890e1f9afe844adf2e251d390e28ac
Source1:	http://www.broadcom.com/docs/linux_sta/hybrid-portsrc-x86_64-v%{version}.tar.gz
# Source1-md5:	ed255d2c98690ef76757d95b2d9e6b32
Source2:	http://www.broadcom.com/docs/linux_sta/README.txt
# Source2-md5:	b3510ce9efc0395021b317f54f645b5d
URL:		http://www.broadcom.com/support/802.11/linux_sta.php
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
These packages contain Broadcom's IEEE 802.11a/b/g/n hybrid Linux
device driver for use with Broadcom's BCM4311-, BCM4312-, BCM4321-,
and BCM4322-based hardware.

%package -n kernel%{_alt_kernel}-net-wl
Summary:	Linux driver for wl
Summary(pl.UTF-8):	Sterownik dla Linuksa do wl
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-net-wl
This is driver for wl for Linux. These packages contain Broadcom's
IEEE 802.11a/b/g/n hybrid Linux device driver for use with Broadcom's
BCM4311-, BCM4312-, BCM4321-, and BCM4322-based hardware.

This package contains Linux module.

%prep
%ifarch %{x8664}
%define		src 1
%else
%define		src 0
%endif
%setup -c -T -q -n %{pname}-%{version} -b%src

cat > Makefile << EOF
obj-m	+= wl.o

wl-objs		:= src/wl/sys/wl_linux.o
wl-objs		+= src/wl/sys/wl_iw.o
wl-objs		+= src/shared/linux_osl.o

EXTRA_CFLAGS	:= -I%{_builddir}/%{pname}-%{version}/src/include
EXTRA_CFLAGS	+= -I%{_builddir}/%{pname}-%{version}/src/wl/sys

EXTRA_LDFLAGS	:= $PWD/lib/wlc_hybrid.o_shipped
EOF

%build
%build_kernel_modules -m wl

%install
rm -rf $RPM_BUILD_ROOT
%install_kernel_modules -m wl -d kernel/net/wireless

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-wl
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-wl
%depmod %{_kernel_ver}

%files -n kernel%{_alt_kernel}-net-wl
%defattr(644,root,root,755)
%doc lib/LICENSE.txt
/lib/modules/%{_kernel_ver}/kernel/net/wireless/*.ko*
