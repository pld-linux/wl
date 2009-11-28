# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

#
# main package.
#
%define		rel	0.1
%define		pname	wl
Summary:	Linux kernel module to BCM network cards
Name:		%{pname}%{_alt_kernel}
Version:	5.10.91.9.3
Release:	%{rel}
License:	other
Group:		Base/Kernel
Source0:	http://www.broadcom.com/docs/linux_sta/hybrid-portsrc-x86_32-v%{version}.tar.gz
# Source0-md5:	15890e1f9afe844adf2e251d390e28ac
Source1:	http://www.broadcom.com/docs/linux_sta/README.txt
# Source1-md5:	b3510ce9efc0395021b317f54f645b5d
URL:		http://www.broadcom.com/support/802.11/linux_sta.php
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
These packages contain Broadcom's IEEE 802.11a/b/g/n hybrid Linux
device driver for use with Broadcom's BCM4311-, BCM4312-, BCM4321-,
and BCM4322-based hardware.

# kernel subpackages.

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
%setup -q -c -n %{pname}-%{version}

cat > Makefile << EOF

obj-m += wl.o

wl-objs            :=
wl-objs            += src/wl/sys/wl_linux.o
wl-objs            += src/wl/sys/wl_iw.o
wl-objs            += src/shared/linux_osl.o

EXTRA_CFLAGS       :=
EXTRA_CFLAGS       += -I%{_builddir}/%{pname}-%{version}/src/include
EXTRA_CFLAGS       += -I%{_builddir}/%{pname}-%{version}/src/wl/sys
EXTRA_CFLAGS += -DCONFIG_MODULE_NAME_SOME_OPTION=1
%{?debug:CFLAGS += -DCONFIG_MODULE_NAME_DEBUG=1}
EOF


%build
%if %{with userspace}


%endif

%if %{with kernel}

%build_kernel_modules -m wl

# modules placed in subdirectory:
# %build_kernel_modules -C -m wl

%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}


%endif

%if %{with kernel}
%install_kernel_modules -m wl -d kernel/net/wireless

# to avoid conflict with in-kernel modules, and prepare modprobe config:
%install_kernel_modules -s current -n NAME -m wl -d kernel/drivers/net/wireless
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-wl
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-wl
%depmod %{_kernel_ver}

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-wl
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/*.ko*
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)

%endif
