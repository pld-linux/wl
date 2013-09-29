# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_with	verbose		# verbose build (V=1)
%bcond_with	dkms	# build dkms package

%define		rel	3
%define		modname	wl
%define		file_ver	%(echo %{version} | tr . _)
Summary:	Broadcom 802.11 a/b/g/n hybrid Linux networking device driver
Name:		kernel%{_alt_kernel}-net-wl
Version:	6.30.223.141
Release:	%{rel}@%{_kernel_ver_str}
License:	other
Group:		Base/Kernel
Source0:	http://www.broadcom.com/docs/linux_sta/hybrid-v35-nodebug-pcoem-%{file_ver}.tar.gz
# Source0-md5:	f4809d9149e8e60ef95021ae93a4bf21
Source1:	http://www.broadcom.com/docs/linux_sta/hybrid-v35_64-nodebug-pcoem-%{file_ver}.tar.gz
# Source1-md5:	039f33d2a3ff2890e42717092d1eb0c4
Source2:	http://www.broadcom.com/docs/linux_sta/README.txt
# Source2-md5:	8a6e8708a5e00ab6d841cde51d70eb1b
Source3:	dkms.conf
Patch0:		broadcom-sta-6.30.223.141-kernel-3.10.patch
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

# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0

%description
These packages contain Broadcom's IEEE 802.11a/b/g/n hybrid Linux
device driver for use with Broadcom's BCM4311-, BCM4312-, BCM4313-,
BCM4321-, BCM4322-, BCM43224-, and BCM43225-, BCM43227- and
BCM43228-based hardware.

This is an Official Release of Broadcom's hybrid Linux driver for use
with Broadcom based hardware.

%package -n dkms-%{modname}
Summary:	DKMS-ready driver for Broadcom WL driver
Group:		Base/Kernel
Release:	%{rel}
Requires(pre):	dkms
Requires(post):	dkms
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n dkms-%{modname}
This package contains a DKMS-ready driver for Broadcom WL driver.

%prep
%ifarch %{x8664}
%define src 1
%else
%define src 0
%endif
%setup -c -T -q -n %{modname}-%{version} -b%{src}
%patch0 -p2

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

cp -p %{SOURCE2} .

cat > Makefile << EOF
obj-m	+= wl.o

wl-objs		+= src/wl/sys/wl_linux.o
wl-objs		+= src/wl/sys/wl_iw.o
wl-objs		+= src/shared/linux_osl.o

EXTRA_CFLAGS	+= -I%{_builddir}/%{modname}-%{version}/src/include
EXTRA_CFLAGS	+= -I%{_builddir}/%{modname}-%{version}/src/common/include
EXTRA_CFLAGS	+= -I%{_builddir}/%{modname}-%{version}/src/wl/sys
EXTRA_CFLAGS	+= -I%{_builddir}/%{modname}-%{version}/src/shared/bcmwifi/include

EXTRA_LDFLAGS	:= $PWD/lib/wlc_hybrid.o_shipped
EOF

%build
%if %{with kernel}
%build_kernel_modules -m wl
%endif

%install
rm -rf $RPM_BUILD_ROOT
%if %{with kernel}
%install_kernel_modules -m wl -d kernel/drivers/net/wireless
%endif

%if %{with dkms}
install -d $RPM_BUILD_ROOT%{_usrsrc}/%{modname}-%{version}-%{rel}
cp -a Makefile lib src $RPM_BUILD_ROOT%{_usrsrc}/%{modname}-%{version}-%{rel}
sed -e 's|@MODNAME@|%{modname}|g' -e 's|@MODVERSION@|%{version}-%{rel}|g' \
	%{SOURCE3} > $RPM_BUILD_ROOT%{_usrsrc}/%{modname}-%{version}-%{rel}/dkms.conf
%endif

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

%post -n dkms-%{modname}
%{_sbindir}/dkms add -m %{modname} -v %{version}-%{rel} --rpm_safe_upgrade && \
%{_sbindir}/dkms build -m %{modname} -v %{version}-%{rel} --rpm_safe_upgrade && \
%{_sbindir}/dkms install -m %{modname} -v %{version}-%{rel} --rpm_safe_upgrade || :

%preun -n dkms-%{modname}
%{_sbindir}/dkms remove -m %{modname} -v %{version}-%{rel} --rpm_safe_upgrade --all || :

%if %{with kernel}
%files
%defattr(644,root,root,755)
%doc lib/LICENSE.txt README.txt
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/*.ko*
%endif

%if %{with dkms}
%files -n dkms-%{modname}
%defattr(644,root,root,755)
%{_usrsrc}/%{modname}-%{version}-%{rel}
%endif
