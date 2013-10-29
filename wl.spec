# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_with	verbose		# verbose build (V=1)
%bcond_with	dkms		# build dkms package

%if %{without kernel}
%undefine	with_dist_kernel
%endif

%if "%{_alt_kernel}" != "%{nil}"
%if 0%{?build_kernels:1}
%{error:alt_kernel and build_kernels are mutually exclusive}
exit 1
%endif
%global		_build_kernels		%{alt_kernel}
%else
%global		_build_kernels		%{?build_kernels:,%{?build_kernels}}
%endif

# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0

%define		kbrs	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo "BuildRequires:kernel%%{_alt_kernel}-module-build >= 3:2.6.20.2" ; done)
%define		kpkg	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo %%kernel_pkg ; done)
%define		bkpkg	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo %%build_kernel_pkg ; done)

%define		rel	4
%define		pname	wl
%define		file_ver	%(echo %{version} | tr . _)
Summary:	Broadcom 802.11 a/b/g/n hybrid Linux networking device driver
Name:		%{pname}%{_alt_kernel}
Version:	6.30.223.141
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
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
BuildRequires:	rpmbuild(macros) >= 1.678
%{?with_dist_kernel:%{expand:%kbrs}}
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
These packages contain Broadcom's IEEE 802.11a/b/g/n hybrid Linux
device driver for use with Broadcom's BCM4311-, BCM4312-, BCM4313-,
BCM4321-, BCM4322-, BCM43224-, and BCM43225-, BCM43227- and
BCM43228-based hardware.

This is an Official Release of Broadcom's hybrid Linux driver for use
with Broadcom based hardware.

%package -n dkms-%{pname}
Summary:	DKMS-ready driver for Broadcom WL driver
Group:		Base/Kernel
Release:	%{rel}
Requires(pre):	dkms
Requires(post):	dkms
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n dkms-%{pname}
This package contains a DKMS-ready driver for Broadcom WL driver.

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-net-wl\
Summary:	Broadcom 802.11 a/b/g/n hybrid Linux networking device driver\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%if %{with dist_kernel}\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
%endif\
\
%description -n kernel%{_alt_kernel}-net-wl\
These packages contain Broadcom's IEEE 802.11a/b/g/n hybrid Linux\
device driver for use with Broadcom's BCM4311-, BCM4312-, BCM4313-,\
BCM4321-, BCM4322-, BCM43224-, and BCM43225-, BCM43227- and\
BCM43228-based hardware.\
\
This is an Official Release of Broadcom's hybrid Linux driver for use\
with Broadcom based hardware.\
\
%files -n kernel%{_alt_kernel}-net-wl\
%defattr(644,root,root,755)\
%doc lib/LICENSE.txt README.txt\
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/*.ko*\
\
%post -n kernel%{_alt_kernel}-net-wl\
%depmod %{_kernel_ver}\
\
%posttrans -n kernel%{_alt_kernel}-net-wl\
%banner -e kernel%{_alt_kernel}-net-wl <<EOF\
WARNING! This kernel module is not GPL licensed.\
Before using it be sure to accept license: %{_docdir}/kernel%{_alt_kernel}-net-wl-%{version}/LICENSE.txt*\
EOF\
\
%postun -n kernel%{_alt_kernel}-net-wl\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%build_kernel_modules -m wl\
%install_kernel_modules -D installed -m wl -d kernel/drivers/net/wireless\
%{nil}

%{?with_kernel:%{expand:%kpkg}}

%prep
%ifarch %{x8664}
%define src 1
%else
%define src 0
%endif
%setup -c -T -q -n %{pname}-%{version} -b%{src}
%patch0 -p2

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

cp -p %{SOURCE2} .

cat > Makefile << 'EOF'
obj-m	+= wl.o

wl-objs		+= src/wl/sys/wl_linux.o
wl-objs		+= src/wl/sys/wl_iw.o
wl-objs		+= src/shared/linux_osl.o

EXTRA_CFLAGS	+= -I$(KBUILD_EXTMOD)/src/include
EXTRA_CFLAGS	+= -I$(KBUILD_EXTMOD)/src/common/include
EXTRA_CFLAGS	+= -I$(KBUILD_EXTMOD)/src/wl/sys
EXTRA_CFLAGS	+= -I$(KBUILD_EXTMOD)/src/shared/bcmwifi/include

EXTRA_LDFLAGS	:= $(KBUILD_EXTMOD)/lib/wlc_hybrid.o_shipped
EOF

%build
%{?with_kernel:%{expand:%bkpkg}}

%install
rm -rf $RPM_BUILD_ROOT
%if %{with kernel}
install -d $RPM_BUILD_ROOT
cp -a installed/* $RPM_BUILD_ROOT
%endif

%if %{with dkms}
install -d $RPM_BUILD_ROOT%{_usrsrc}/%{pname}-%{version}-%{rel}
cp -a Makefile lib src $RPM_BUILD_ROOT%{_usrsrc}/%{pname}-%{version}-%{rel}
sed -e 's|@pname@|%{pname}|g' -e 's|@MODVERSION@|%{version}-%{rel}|g' \
	%{SOURCE3} > $RPM_BUILD_ROOT%{_usrsrc}/%{pname}-%{version}-%{rel}/dkms.conf
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n dkms-%{pname}
%{_sbindir}/dkms add -m %{pname} -v %{version}-%{rel} --rpm_safe_upgrade && \
%{_sbindir}/dkms build -m %{pname} -v %{version}-%{rel} --rpm_safe_upgrade && \
%{_sbindir}/dkms install -m %{pname} -v %{version}-%{rel} --rpm_safe_upgrade || :

%preun -n dkms-%{pname}
%{_sbindir}/dkms remove -m %{pname} -v %{version}-%{rel} --rpm_safe_upgrade --all || :

%if %{with dkms}
%files -n dkms-%{pname}
%defattr(644,root,root,755)
%{_usrsrc}/%{pname}-%{version}-%{rel}
%endif
