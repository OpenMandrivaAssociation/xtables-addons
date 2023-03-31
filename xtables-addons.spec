%define accountmajor 0
%define libaccount %mklibname account %{accountmajor}
%define libaccountdevel %mklibname account -d

Name:		xtables-addons
Version:	3.13
Release:	2
Summary:	Extensions that were not, or are not yet, accepted in the main kernel/iptables packages
Group:		System/Kernel and hardware
License:	GPLv2
URL:		http://xtables-addons.sourceforge.net/
Source0: 	https://inai.de/files/xtables-addons/%{name}-%{version}.tar.xz
Provides:	iptables-addons = %{version}-%{release}
BuildRequires:	pkgconfig(xtables) >= 1.4.5
BuildRequires:	kernel >= 3.7
Requires:	kernel >= 3.7
Recommends:	iptaccount
Recommends:	xtables-geoip

%description
Xtables-addons is the successor to patch-o-matic(-ng). Likewise, it contains
extensions that were not, or are not yet, accepted in the main kernel/iptables
packages.

Xtables-addons is different from patch-o-matic in that you do not have to
patch or recompile the kernel, sometimes recompiling iptables is also not
needed. But please see the INSTALL file for the minimum requirements of this
package.

(The name stems from Xtables, which is the protocol-agnostic code part of the
table-based firewalling schema.)

%package -n iptaccount
Summary:	Helper example program for iptables accounting
Group:		System/Kernel and hardware
Requires:	%{libaccount} = %{EVRD}

%description -n iptaccount
Helper example program for iptables accounting using the ACCOUNT target.

%package -n xtables-geoip
Summary:	Helper scripts for using geoip in iptables
Group:		System/Kernel and hardware
Requires:	kmod(xt_geoip.ko) = %{version}
Requires:	%{name} = %{EVRD}
BuildArch:	noarch

%description -n xtables-geoip
Helper scripts for using geoip in iptables.

%package -n %{libaccount}
Summary:	Library for iptaccount
Group:		System/Kernel and hardware
Requires:	kmod(xt_ACCOUNT.ko) = %{version}
Requires:	%{name} = %{EVRD}

%description -n %{libaccount}
Library for iptaccount. iptaccount is a helper example program for iptables
accounting using the ACCOUNT target.

%package -n %{libaccountdevel}
Summary:	Development library for iptaccount
Group:		System/Kernel and hardware
Requires:	%{libaccount} = %{EVRD}

%description -n %{libaccountdevel}
Development library for iptaccount. iptaccount is a helper example program
for iptables accounting using the ACCOUNT target.

%package -n dkms-%{name}
Summary:	dkms package for xtables-addons
Group:		System/Kernel and hardware
Provides:	kmod(xt_geoip.ko) = %{version}
Provides:	kmod(xt_ACCOUNT.ko) = %{version}
Requires:	kernel-devel >= 3.7
Requires:	dkms >= 2.0.19-37
Requires(post):	dkms >= 2.0.19-37
Requires(preun):	dkms >= 2.0.19-37

%description -n dkms-%{name}
This contains the dkms package building the xtables-addons kernel modules.

Xtables-addons is the successor to patch-o-matic(-ng). Likewise, it contains
extensions that were not, or are not yet, accepted in the main kernel/iptables
packages.

Xtables-addons is different from patch-o-matic in that you do not have to
patch or recompile the kernel, sometimes recompiling iptables is also not
needed. But please see the INSTALL file for the minimum requirements of this
package.

(The name stems from Xtables, which is the protocol-agnostic code part of the
table-based firewalling schema.)

%prep
%autosetup -p1

%build
# don't build the modules
%configure --without-kbuild
%make_build

%install
%make_install

# we don't package .la
rm -f %{buildroot}%{_libdir}/libxt_ACCOUNT_cl.la

# prepare the dkms sources
mkdir -p %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/ACCOUNT %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/pknock
cp extensions/Kbuild extensions/Mbuild mconfig extensions/Makefile* extensions/mac.c extensions/xt_* extensions/compat_* %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}
cp extensions/ACCOUNT/Kbuild extensions/ACCOUNT/Mbuild extensions/ACCOUNT/Makefile* extensions/ACCOUNT/xt_* %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/ACCOUNT
cp extensions/pknock/Kbuild extensions/pknock/Mbuild extensions/pknock/Makefile* extensions/pknock/xt_* %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/pknock

# mconfig is not in parent dir anymore
sed -i 's/${XA_ABSTOPSRCDIR}/${M}/' %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/Kbuild

# remove ipset-6 references to silence make clean errors
sed -i '/ipset-6/ d' %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/Kbuild
sed -i '/ipset-6/ d' %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/Mbuild

cat > %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/dkms.conf << EOF
PACKAGE_NAME="%{name}"
PACKAGE_VERSION="%{version}-%{release}"
AUTOINSTALL="yes"
MAKE[0]="'make' -j\${parallel_jobs} -C \${kernel_source_dir} M=\\\$(pwd)"
CLEAN="make -C \${kernel_source_dir} M=\\\$(pwd) clean"
BUILT_MODULE_LOCATION[0]="ACCOUNT"
DEST_MODULE_LOCATION[0]="/kernel/extra"
BUILT_MODULE_NAME[0]="xt_ACCOUNT"
BUILT_MODULE_LOCATION[1]="pknock"
DEST_MODULE_LOCATION[1]="/kernel/extra"
BUILT_MODULE_NAME[1]="xt_pknock"
EOF

i=2
for mod in compat_xtables xt_CHAOS \
xt_condition xt_DELUDE xt_DHCPMAC xt_DNETMAP xt_fuzzy xt_geoip xt_iface \
xt_IPMARK xt_ipp2p xt_ipv4options xt_length2 xt_LOGMARK xt_lscan xt_psd \
xt_quota2 xt_SYSRQ xt_TARPIT; do
    echo -e "DEST_MODULE_LOCATION[$i]=\"/kernel/extra\"\nBUILT_MODULE_NAME[$i]=\"$mod\"" >> %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/dkms.conf
    (( i = $i + 1 ))
done

%post -n dkms-%{name}
    set -x
    /usr/sbin/dkms add     -m %{name} -v %{version}-%{release} --rpm_safe_upgrade
if [ -z "$DURING_INSTALL" ] ; then
    /usr/sbin/dkms build   -m %{name} -v %{version}-%{release} --rpm_safe_upgrade &&
    /usr/sbin/dkms install -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --force
    true
fi

%preun -n dkms-%{name}
set -x
/usr/sbin/dkms remove  -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --all
true

%files
%doc LICENSE README INSTALL
%{_sbindir}/pknlusr
%{_libdir}/xtables/libxt_*.so
%{_mandir}/man8/xtables-addons.8.*
%{_mandir}/man8/pknlusr.8.*

%files -n dkms-%{name}
%{_usr}/src/%{name}-%{version}-%{release}

%files -n iptaccount
%{_sbindir}/iptaccount
%{_mandir}/man8/iptaccount.8*

%files -n %libaccount
%{_libdir}/libxt_ACCOUNT_cl.so.%{accountmajor}
%{_libdir}/libxt_ACCOUNT_cl.so.%{accountmajor}.*

%files -n %libaccountdevel
%{_libdir}/libxt_ACCOUNT_cl.so

%files -n xtables-geoip
%{_bindir}/xt_geoip_fetch
%{_bindir}/xt_geoip_fetch_maxmind
%{_libexecdir}/xtables-addons/xt_geoip_build
%{_libexecdir}/xtables-addons/xt_geoip_dl
%{_libexecdir}/xtables-addons/xt_geoip_build_maxmind
%{_libexecdir}/xtables-addons/xt_geoip_dl_maxmind
%{_mandir}/man1/xt_geoip_build.1*
%{_mandir}/man1/xt_geoip_dl.1*
%{_mandir}/man1/xt_geoip_fetch.1.*
