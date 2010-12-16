# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	verbose		# verbose build (V=1)

%define		_enable_debug_packages	0

%define		rel	1
%define		pname	wl
Summary:	Linux kernel module to BCM network cards
Name:		%{pname}%{_alt_kernel}
Version:	5.60.246.6
Release:	%{rel}
License:	other
Group:		Base/Kernel
Source0:	http://www.broadcom.com/docs/linux_sta/hybrid-portsrc_x86-32_v%{version}.tar.gz
# Source0-md5:	1d2561cfe5d6c72ab6838a35de4010db
Source1:	http://www.broadcom.com/docs/linux_sta/hybrid-portsrc_x86-64_v%{version}.tar.gz
# Source1-md5:	790a85a298995922fcdd5a209b9873df
Source2:	http://www.broadcom.com/docs/linux_sta/README.txt
# Source2-md5:	04b0c96665b520709811a0c80a9e8ef5
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
%install_kernel_modules -m wl -d kernel/drivers/net/wireless
install %{SOURCE2} .

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-wl
%depmod %{_kernel_ver}

%posttrans -n kernel%{_alt_kernel}-net-wl
%banner -e kernel%{_alt_kernel}-net-wl <<EOF
WARNING! That is not GPL software. 
Before you use it read /usr/share/doc/kernel-net-wl-%{version}/LICENSE.txt.gz
EOF

%postun	-n kernel%{_alt_kernel}-net-wl
%depmod %{_kernel_ver}

%files -n kernel%{_alt_kernel}-net-wl
%defattr(644,root,root,755)
%doc lib/LICENSE.txt README.txt
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/*.ko*
