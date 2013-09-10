# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	verbose		# verbose build (V=1)

%define		rel	17
%define		pname	wl
%define		file_ver	%(echo %{version} | tr . _)
Summary:	Broadcom 802.11 a/b/g/n hybrid Linux networking device driver
Name:		kernel%{_alt_kernel}-net-wl
Version:	5.100.82.112
Release:	%{rel}@%{_kernel_ver_str}
License:	other
Group:		Base/Kernel
Source0:	http://www.broadcom.com/docs/linux_sta/hybrid-portsrc_x86_32-v%{file_ver}.tar.gz
# Source0-md5:	62d04d148b99f993ef575a71332593a9
Source1:	http://www.broadcom.com/docs/linux_sta/hybrid-portsrc_x86_64-v%{file_ver}.tar.gz
# Source1-md5:	310d7ce233a9a352fbe62c451b2ea309
Source2:	http://www.broadcom.com/docs/linux_sta/README.txt
# Source2-md5:	6fd54aac59a53559d01520f35500693b
Patch1:		kernel-net-wl-linux-3.2.patch
Patch2:		kernel-net-wl-linux-3.4.patch
Patch3:		kernel-net-wl-linux-3.10.patch
URL:		http://www.broadcom.com/support/802.11/linux_sta.php
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_enable_debug_packages	0

%description
These packages contain Broadcom's IEEE 802.11a/b/g/n hybrid Linux
device driver for use with Broadcom's BCM4311-, BCM4312-, BCM4313-,
BCM4321-, BCM4322-, BCM43224-, and BCM43225-, BCM43227- and
BCM43228-based hardware.

%prep
%ifarch %{x8664}
%define src 1
%else
%define src 0
%endif
%setup -c -T -q -n %{pname}-%{version} -b%src
%patch1 -p0
%patch2 -p0
%patch3 -p1

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

%post
%depmod %{_kernel_ver}

%posttrans
%banner -e kernel%{_alt_kernel}-net-wl <<EOF
WARNING! This kernel module is not GPL licensed.
Before using it be sure to accept license: %{_docdir}/kernel%{_alt_kernel}-net-wl-%{version}/LICENSE.txt*
EOF

%postun
%depmod %{_kernel_ver}

%files
%defattr(644,root,root,755)
%doc lib/LICENSE.txt README.txt
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/*.ko*
