# Conditional build:
%bcond_without	kernel		# don't build kernel modules
%bcond_with	verbose		# verbose build (V=1)
%bcond_without	userspace	# don't build userspace programs
%bcond_without	dkms		# build dkms package

%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if %{without userspace}
%undefine	with_dkms
%endif

# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0

%define		_duplicate_files_terminate_build	0

%define		rel	21
%define		pname	wl
%define		file_ver	%(echo %{version} | tr . _)
Summary:	Broadcom 802.11 a/b/g/n hybrid Linux networking device driver
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	6.30.223.271
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	other
Group:		Base/Kernel
Source0:	http://www.broadcom.com/docs/linux_sta/hybrid-v35-nodebug-pcoem-%{file_ver}.tar.gz
# Source0-md5:	4e75f4cb7d87f690f9659ffc478495f0
Source1:	http://www.broadcom.com/docs/linux_sta/hybrid-v35_64-nodebug-pcoem-%{file_ver}.tar.gz
# Source1-md5:	115903050c41d466161784d4c843f4f9
Source2:	http://www.broadcom.com/docs/linux_sta/README.txt
# Source2-md5:	8a6e8708a5e00ab6d841cde51d70eb1b
Source3:	dkms.conf
Source4:	modprobe.conf
Patch0:		13-broadcom-sta-6.30.223.248-linux-3.18-null-pointer-crash.patch
Patch1:		gcc-4.9.patch
Patch2:		no-dead-code.patch
Patch3:		linux-4.7.patch
Patch4:		linux-4.8.patch
Patch5:		17-fix-kernel-warnings.patch
Patch6:		linux-4.11.patch
Patch7:		linux-4.12.patch
Patch8:		008-linux415.patch
Patch9:		kernel-4.14.patch
Patch10:	linux-5.6.patch
Patch11:	kernel-5.10.patch
Patch12:	kernel-5.17.patch
Patch13:	kernel-5.18.patch
Patch14:	kernel-6.0.patch
Patch15:	kernel-6.1.patch
Patch16:	kernel-6.12.patch
Patch17:	kernel-6.13.patch
URL:		http://www.broadcom.com/support/802.11
BuildRequires:	rpmbuild(macros) >= 1.701
%{?with_kernel:%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:2.6.20.2}}
ExclusiveArch:	%{ix86} %{x8664} x32
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
BuildArch:	noarch

%description -n dkms-%{pname}
This package contains a DKMS-ready driver for Broadcom WL driver.

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-net-wl\
Summary:	Broadcom 802.11 a/b/g/n hybrid Linux networking device driver\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
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
%doc wl/lib/LICENSE.txt README.txt\
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/*.ko*\
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/%{pname}.conf\
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
%{__make} -C wl KERNELRELEASE=%{_kernel_ver} KBUILD_DIR=%{_kernelsrcdir} clean\
%{__make} -C wl KERNELRELEASE=%{_kernel_ver} KBUILD_DIR=%{_kernelsrcdir}\
%install_kernel_modules -D installed -m wl/wl -d kernel/drivers/net/wireless\
%{nil}

%{?with_kernel:%{expand:%create_kernel_packages}}

%prep
%ifarch %{x8664} x32
%define src 1
%else
%define src 0
%endif
%setup -c -q -n %{pname}-%{version} -a %{src}
%patch -P 0 -p1
%patch -P 1 -p1
%patch -P 2 -p1
%patch -P 3 -p1
%patch -P 4 -p1
%patch -P 5 -p2
%patch -P 6 -p1
%patch -P 7 -p1
%patch -P 8 -p1
%patch -P 9 -p1
%patch -P 10 -p2
%patch -P 11 -p1
%patch -P 12 -p2
%patch -P 13 -p2
%patch -P 14 -p2
%patch -P 15 -p2
%patch -P 16 -p2
%patch -P 17 -p2

mkdir wl
mv lib src Makefile wl/
cp -p %{SOURCE2} .

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

%build
%{?with_kernel:%{expand:%build_kernel_packages}}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/modprobe.d

%if %{with kernel}
install -d $RPM_BUILD_ROOT
cp -a installed/* $RPM_BUILD_ROOT
cp -p %{SOURCE4} $RPM_BUILD_ROOT/etc/modprobe.d/%{pname}.conf
%endif

%if %{with dkms}
install -d $RPM_BUILD_ROOT%{_usrsrc}/%{pname}-%{version}-%{rel}
cp -a wl/Makefile wl/lib wl/src $RPM_BUILD_ROOT%{_usrsrc}/%{pname}-%{version}-%{rel}
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
