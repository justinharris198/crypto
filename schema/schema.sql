drop table if exists cryptoTotalPricingExt;
drop table if exists cryptoRepoUpdateDatesExt;
drop table if exists cryptoReposExt;
drop table if exists cryptoErrorsExt;
drop table if exists cryptoAllBittrexMarketsExt;

create table cryptoTotalPricingExt (
	cryptoTotalPricingExtId int primary key identity,
	date datetime,
	ticker varchar(255),
	openPrice float(53),
	highPrice float(53),
	lowPrice float(53),
	closePrice float(53),
	volume float(53),
	created datetime default getDate(),
	modified datetime default getDate()

);
create table cryptoRepoUpdateDatesExt (
	cryptoRepoUpdateDatesExtId int primary key identity,
	author varchar(255),
	market varchar(255),
	repoName varchar(255),
	updated datetime,
	created datetime default getDate(),
	modified datetime default getDate()
);
create table cryptoReposExt (
	cryptoReposExtId int primary key identity,
	longName varchar(255),
	repoLocation varchar(255),
	repoName varchar(255),
	shortName varchar(255),
	created datetime default getDate(),
	modified datetime default getDate()
);
create table cryptoErrorsExt (
	cryptoErrorsExtId int primary key identity,
	longName  varchar(255),
	shortName varchar(255),
	error varchar(255),
	output varchar(2555),
	created datetime default getDate(),
	modified datetime default getDate()
);
create table cryptoAllBittrexMarketsExt (
	cryptoAllBittrexMarketsExtId int primary key identity,
	baseCurrency varchar(255),
	baseCurrencyLong varchar(255),
	coinType varchar(255),
	createdBittrex datetime,
	isActive  varchar(255),
	isRestricted varchar(255),
	isSponsored varchar(255),
	logoUrl varchar(255),
	marketCurrency varchar(255),
	marketCurrencyLong varchar(255),
	marketName varchar(255),
	minTradeSize float(53),
	notice varchar(2555),
	txFee float(53),
	created datetime default getDate(),
	modified datetime default getDate()
);