%define accountmajor	0
%define libaccount	%mklibname account %{accountmajor}
%define libaccountdevel	%mklibname account -d

Name:		xtables-addons
Version:	3.7
Release:	2
Summary:	Extensions that were not, or are not yet, accepted in the main kernel/iptables packages
Group:		System/Kernel and hardware
License:	GPLv2
URL:		http://xtables-addons.sourceforge.net/
Source0: 	http://downloads.sourceforge.net/xtables-addons/%{name}-%{version}.tar.xz

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
Requires:	%{libaccount} == %{version}-%{release}

%description -n iptaccount
Helper example program for iptables accounting using the ACCOUNT target.


%package -n xtables-geoip
Summary:	Helper scripts for using geoip in iptables
Group:		System/Kernel and hardware
Requires:       kmod(xt_geoip.ko) = %{version}
Requires:       %{name} = %{version}-%{release}
BuildArch:	noarch

%description -n xtables-geoip
Helper scripts for using geoip in iptables.


%package -n %{libaccount}
Summary:	Library for iptaccount
Group:		System/Kernel and hardware
Requires:       kmod(xt_ACCOUNT.ko) = %{version}
Requires:       %{name} = %{version}-%{release}

%description -n %{libaccount}
Library for iptaccount. iptaccount is a helper example program for iptables
accounting using the ACCOUNT target.


%package -n %{libaccountdevel}
Summary:	Development library for iptaccount
Group:		System/Kernel and hardware
Requires:	%{libaccount} == %{version}-%{release}

%description -n %{libaccountdevel}
Development library for iptaccount. iptaccount is a helper example program
for iptables accounting using the ACCOUNT target.


%package -n dkms-%{name}
Summary:	dkms package for xtables-addons
Group:		System/Kernel and hardware
Provides:       kmod(xt_geoip.ko) = %{version}
Provides:       kmod(xt_ACCOUNT.ko) = %{version}
Requires:	kernel-devel >= 3.7
Requires:	dkms >= 2.0.19-37
Requires(post):	dkms >= 2.0.19-37
Requires(preun):dkms >= 2.0.19-37

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
%configure --without-kbuild --libdir="/%{_lib}"
%make_build

%install
%make_install

# we don't package .la
rm -f %{buildroot}/%{_lib}/libxt_ACCOUNT_cl.la

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
MAKE[0]="'make' -j\${parallel_jobs} -C \${kernel_source_dir}"
CLEAN="make -C \${kernel_source_dir} clean"
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

cat > README.omv <<EOF

NOTE1: Be careful, since the xt_ACCOUNT module seems not to be loaded, if
you have shorewall, you'll need to put this module in shorewalls
modules.xtables file.

NOTE2: if you're using shorewall, you can put the following in the
/etc/shorewall/accounting file:

SECTION PREROUTING
ACCOUNT(down,0.0.0.0/0)		-	eth0	-
ACCOUNT(local,192.168.0.0/24)	-	eth1	-
SECTION POSTROUTING
ACCOUNT(up,0.0.0.0/0)		-	-	eth0
ACCOUNT(local,192.168.0.0/24)	-	-	eth1

(assuming you have a LAN 192.168.0.0/24 on eth1 and internet on eth0)

[]# iptables -l down (will show your total downstream traffic in the src)
[]# iptables -l up (will show your total upstream traffic in the src section)
[]# iptables -l local (will show your up/downstream traffic per ip address)

(special case 0.0.0.0/0 will have all traffic always in src)

EOF

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
/%{_lib}/xtables/libxt_*.so
%{_mandir}/man8/xtables-addons.8.xz

%files -n dkms-%{name}
%{_usr}/src/%{name}-%{version}-%{release}

%files -n iptaccount
%doc README.omv
%{_sbindir}/iptaccount
%{_mandir}/man8/iptaccount.8*

%files -n %libaccount
%{_libdir}/libxt_ACCOUNT_cl.so.%{accountmajor}
%{_libdir}/libxt_ACCOUNT_cl.so.%{accountmajor}.*

%files -n %libaccountdevel
%{_libdir}/libxt_ACCOUNT_cl.so

%files -n xtables-geoip
%{_libexecdir}/xtables-addons/xt_geoip_build
%{_libexecdir}/xtables-addons/xt_geoip_dl
%{_mandir}/man1/xt_geoip_build.1*
%{_mandir}/man1/xt_geoip_dl.1*
