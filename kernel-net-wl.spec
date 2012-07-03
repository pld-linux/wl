# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	verbose		# verbose build (V=1)

%define		_enable_debug_packages	0

%define		rel	2
%define		pname	wl
Summary:	Linux kernel module for BCM network cards
Name:		%{pname}%{_alt_kernel}
Version:	5.100.82.38
%define		file_ver	%(echo %{version} | tr . _)
Release:	%{rel}
License:	other
Group:		Base/Kernel
Source0:	http://www.broadcom.com/docs/linux_sta/hybrid-portsrc_x86_32-v%{file_ver}.tar.gz
# Source0-md5:	c0074a1622c75916442e26763ddf47d0
Source1:	http://www.broadcom.com/docs/linux_sta/hybrid-portsrc_x86_64-v%{file_ver}.tar.gz
# Source1-md5:	cac172f7422fa43264049c7065fe21d6
Source2:	http://www.broadcom.com/docs/linux_sta/README.txt
# Source2-md5:	24976921c7b8854ed2cd56fbc5b1c13c
Patch0:		broadcom-sta_4_kernel-2.6.37.patch
Patch1:		kernel-net-wl-linux-3.2.patch
Patch2:		kernel-net-wl-linux-3.4.patch
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
%patch0 -p0
%patch1 -p0
%patch2 -p0

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
%install_kernel_modules -m wl -d kernel/drivers/net/wireless
install %{SOURCE2} .

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-wl
%depmod %{_kernel_ver}

%posttrans -n kernel%{_alt_kernel}-net-wl
%banner -e kernel%{_alt_kernel}-net-wl <<EOF
WARNING! This kernel module is not GPL licensed.
Before using it be sure to accept license: %{_docdir}/kernel%{_alt_kernel}-net-wl-%{version}/LICENSE.txt*
EOF

%postun	-n kernel%{_alt_kernel}-net-wl
%depmod %{_kernel_ver}

%files -n kernel%{_alt_kernel}-net-wl
%defattr(644,root,root,755)
%doc lib/LICENSE.txt README.txt
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/*.ko*
