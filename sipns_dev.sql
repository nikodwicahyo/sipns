-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Waktu pembuatan: 05 Jun 2026 pada 06.19
-- Versi server: 8.0.30
-- Versi PHP: 8.2.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sipns_dev`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data untuk tabel `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('85cddd831f8c');

-- --------------------------------------------------------

--
-- Struktur dari tabel `audit_log`
--

CREATE TABLE `audit_log` (
  `id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `action` varchar(50) NOT NULL,
  `table_name` varchar(50) NOT NULL,
  `record_id` int DEFAULT NULL,
  `description` text,
  `ip_address` varchar(45) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data untuk tabel `audit_log`
--

INSERT INTO `audit_log` (`id`, `user_id`, `action`, `table_name`, `record_id`, `description`, `ip_address`, `created_at`) VALUES
(1, 1, 'UPDATE', 'guru', 1, 'Edit guru Dr. Siti Rahmawati', '127.0.0.1', '2026-06-04 08:37:50'),
(2, 1, 'UPDATE', 'guru', 3, 'Edit guru Dewi Sartika, S.Si.', '127.0.0.1', '2026-06-04 08:38:02'),
(3, 1, 'INSERT', 'guru', 4, 'Tambah guru Niko Dwicahyo (TIK)', '127.0.0.1', '2026-06-04 08:38:19'),
(4, 1, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas X-IPA-1', '127.0.0.1', '2026-06-04 08:50:08'),
(5, 1, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas X-IPA-1', '127.0.0.1', '2026-06-04 08:50:08'),
(6, 1, 'EXPORT_EXCEL', 'nilai', NULL, 'Ekspor Excel nilai kelas X-IPA-1', '127.0.0.1', '2026-06-04 08:52:09'),
(7, 1, 'UPDATE', 'siswa', 1, 'Edit siswa Budi Santoso (NIS: 2024001)', '127.0.0.1', '2026-06-04 11:09:59'),
(8, 1, 'PRINT_PDF', 'nilai', 8, 'Cetak PDF transkrip Hendra Gunawan', '127.0.0.1', '2026-06-04 11:10:32'),
(9, 1, 'PRINT_PDF', 'nilai', 8, 'Cetak PDF transkrip Hendra Gunawan', '127.0.0.1', '2026-06-04 11:10:35'),
(10, 1, 'INSERT', 'siswa', 11, 'Tambah siswa Niko Dwicahyo  (NIS: 202612379)', '127.0.0.1', '2026-06-04 11:31:06'),
(11, 1, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas 4IA08', '127.0.0.1', '2026-06-04 11:35:22'),
(12, 1, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas 4IA08', '127.0.0.1', '2026-06-04 11:35:24'),
(13, 1, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas X-IPA-1', '127.0.0.1', '2026-06-04 11:35:58'),
(14, 1, 'EXPORT_EXCEL', 'nilai', NULL, 'Ekspor Excel nilai kelas 4IA08', '127.0.0.1', '2026-06-04 11:36:27'),
(15, 1, 'EXPORT_EXCEL', 'nilai', NULL, 'Ekspor Excel nilai kelas X-IPA-1', '127.0.0.1', '2026-06-04 11:36:52'),
(16, 1, 'EXPORT_EXCEL', 'nilai', NULL, 'Ekspor Excel nilai kelas X-IPA-2', '127.0.0.1', '2026-06-04 11:36:59'),
(17, 1, 'DELETE', 'siswa', 11, 'Hapus siswa Niko Dwicahyo  (NIS: 202612379)', '127.0.0.1', '2026-06-04 11:53:14'),
(18, 1, 'INSERT', 'guru', 5, 'Tambah guru Dwi (IPS)', '127.0.0.1', '2026-06-04 11:53:46'),
(19, 1, 'INSERT', 'siswa', 12, 'Tambah siswa Niko Dwicahyo (NIS: 20260292)', '127.0.0.1', '2026-06-04 11:54:27'),
(20, 4, 'INSERT', 'nilai', 25, 'Nilai PAI untuk siswa ID 12', '127.0.0.1', '2026-06-04 11:57:42'),
(21, 4, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas 4IA08', '127.0.0.1', '2026-06-04 11:58:36'),
(22, 4, 'UPDATE', 'nilai', 3, 'Kunci nilai IPA siswa ID 1', '127.0.0.1', '2026-06-04 12:03:07'),
(23, 1, 'DELETE', 'guru', 4, 'Hapus guru Niko Dwicahyo', '127.0.0.1', '2026-06-04 12:03:47'),
(24, 1, 'DELETE', 'guru', 5, 'Hapus guru Dwi', '127.0.0.1', '2026-06-04 12:03:50'),
(25, 1, 'INSERT', 'siswa', 13, 'Tambah siswa Niko Dwicahyo Widiyanto (NIS: 2026029)', '127.0.0.1', '2026-06-04 16:09:38'),
(26, 1, 'INSERT', 'guru', 11, 'Tambah guru Niko Dwicahyo (TIK)', '127.0.0.1', '2026-06-04 16:12:10'),
(27, 1, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas 4IA08', '127.0.0.1', '2026-06-04 16:13:27'),
(28, 1, 'EXPORT_EXCEL', 'nilai', NULL, 'Ekspor Excel nilai kelas 4IA08', '127.0.0.1', '2026-06-04 16:13:57'),
(29, 1, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas 4IA08', '127.0.0.1', '2026-06-04 16:15:08'),
(30, 1, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas 4IA08', '127.0.0.1', '2026-06-04 16:15:19'),
(31, 1, 'INSERT', 'siswa', 14, 'Tambah siswa Bambang (NIS: 20260291)', '127.0.0.1', '2026-06-04 16:38:34'),
(32, 1, 'INSERT', 'guru', 12, 'Tambah guru Sukirna (PJOK)', '127.0.0.1', '2026-06-04 16:40:13'),
(33, 1, 'DELETE', 'users', 16, 'Hapus user 202612379 (siswa)', '127.0.0.1', '2026-06-04 16:41:08'),
(34, 1, 'UPDATE', 'users', 15, 'Edit user GR-004', '127.0.0.1', '2026-06-04 16:41:22'),
(35, 1, 'UPDATE', 'users', 20, 'Reset password user GR-006', '127.0.0.1', '2026-06-04 16:42:15'),
(36, 2, 'INSERT', 'nilai', 26, 'Nilai IPA untuk siswa ID 14', '127.0.0.1', '2026-06-04 16:47:50'),
(37, 2, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas XII-IPA-3', '127.0.0.1', '2026-06-04 16:48:08'),
(38, 2, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas XII-IPA-3', '127.0.0.1', '2026-06-04 16:48:09'),
(39, 2, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas X-IPA-1', '127.0.0.1', '2026-06-04 16:48:24'),
(40, 2, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas X-IPA-1', '127.0.0.1', '2026-06-04 16:48:26'),
(41, 2, 'EXPORT_EXCEL', 'nilai', NULL, 'Ekspor Excel nilai kelas X-IPA-1', '127.0.0.1', '2026-06-04 16:48:49'),
(42, 1, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas X-IPA-1', '127.0.0.1', '2026-06-05 00:44:03'),
(43, 1, 'PRINT_PDF', 'nilai', NULL, 'Cetak PDF rekap nilai kelas X-IPA-1', '127.0.0.1', '2026-06-05 00:44:05'),
(44, 1, 'EXPORT_EXCEL', 'nilai', NULL, 'Ekspor Excel nilai kelas X-IPA-2', '127.0.0.1', '2026-06-05 00:44:34');

-- --------------------------------------------------------

--
-- Struktur dari tabel `guru`
--

CREATE TABLE `guru` (
  `id` int NOT NULL,
  `id_guru` varchar(20) NOT NULL,
  `nama_guru` varchar(100) NOT NULL,
  `mata_pelajaran` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data untuk tabel `guru`
--

INSERT INTO `guru` (`id`, `id_guru`, `nama_guru`, `mata_pelajaran`, `created_at`, `updated_at`, `deleted_at`) VALUES
(1, 'GR-001', 'Dr. Siti Rahmawati', 'IPA', '2026-06-04 01:14:20', '2026-06-04 08:37:50', NULL),
(2, 'GR-002', 'Ahmad Fauzi, S.Pd.', 'Bahasa Indonesia', '2026-06-04 01:14:20', '2026-06-04 01:14:20', NULL),
(3, 'GR-003', 'Dewi Sartika, S.Si.', 'PAI', '2026-06-04 01:14:20', '2026-06-04 08:38:02', NULL),
(4, 'GR-004', 'Niko Dwicahyo', 'TIK', '2026-06-04 08:38:19', '2026-06-04 12:03:47', '2026-06-04 12:03:47'),
(5, 'GR-005', 'Dwi', 'IPS', '2026-06-04 11:53:46', '2026-06-04 12:03:50', '2026-06-04 12:03:50'),
(11, 'GR-006', 'Niko Dwicahyo', 'TIK', '2026-06-04 16:12:10', '2026-06-04 16:12:10', NULL),
(12, 'GR-007', 'Sukirna', 'PJOK', '2026-06-04 16:40:12', '2026-06-04 16:40:12', NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `nilai`
--

CREATE TABLE `nilai` (
  `id` int NOT NULL,
  `siswa_id` int NOT NULL,
  `guru_id` int NOT NULL,
  `mata_pelajaran` varchar(100) NOT NULL,
  `nilai_tugas` decimal(5,2) NOT NULL,
  `nilai_uts` decimal(5,2) NOT NULL,
  `nilai_uas` decimal(5,2) NOT NULL,
  `nilai_akhir` decimal(5,2) DEFAULT NULL,
  `status_lulus` tinyint(1) DEFAULT NULL,
  `is_locked` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ;

--
-- Dumping data untuk tabel `nilai`
--

INSERT INTO `nilai` (`id`, `siswa_id`, `guru_id`, `mata_pelajaran`, `nilai_tugas`, `nilai_uts`, `nilai_uas`, `nilai_akhir`, `status_lulus`, `is_locked`, `created_at`, `updated_at`) VALUES
(1, 1, 1, 'Matematika', 85.00, 78.00, 82.00, 81.70, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(2, 1, 2, 'Bahasa Indonesia', 90.00, 85.00, 88.00, 87.70, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(3, 1, 3, 'IPA', 75.00, 80.00, 78.00, 77.70, 1, 1, '2026-06-04 01:14:22', '2026-06-04 12:03:07'),
(4, 2, 1, 'Matematika', 70.00, 75.00, 72.00, 72.30, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(5, 2, 2, 'Bahasa Indonesia', 88.00, 82.00, 85.00, 85.00, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(6, 2, 3, 'IPA', 65.00, 70.00, 68.00, 67.70, 0, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(7, 3, 1, 'Matematika', 92.00, 88.00, 90.00, 90.00, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(8, 3, 2, 'Bahasa Indonesia', 78.00, 80.00, 75.00, 77.40, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(9, 3, 3, 'IPA', 85.00, 82.00, 86.00, 84.50, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(10, 4, 1, 'Matematika', 60.00, 55.00, 58.00, 57.70, 0, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(11, 4, 2, 'Bahasa Indonesia', 70.00, 65.00, 68.00, 67.70, 0, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(12, 4, 3, 'IPA', 55.00, 60.00, 50.00, 54.50, 0, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(13, 5, 1, 'Matematika', 80.00, 78.00, 85.00, 81.40, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(14, 5, 2, 'Bahasa Indonesia', 75.00, 70.00, 72.00, 72.30, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(15, 6, 1, 'Matematika', 95.00, 90.00, 92.00, 92.30, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(16, 6, 2, 'Bahasa Indonesia', 82.00, 85.00, 80.00, 82.10, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(17, 7, 1, 'Matematika', 68.00, 72.00, 70.00, 70.00, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(18, 7, 2, 'Bahasa Indonesia', 77.00, 75.00, 80.00, 77.60, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(19, 8, 1, 'Matematika', 50.00, 45.00, 55.00, 50.50, 0, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(20, 8, 2, 'Bahasa Indonesia', 60.00, 58.00, 62.00, 60.20, 0, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(21, 9, 1, 'Matematika', 88.00, 85.00, 90.00, 87.90, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(22, 9, 2, 'Bahasa Indonesia', 92.00, 88.00, 85.00, 88.00, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(23, 10, 1, 'Matematika', 72.00, 68.00, 75.00, 72.00, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(24, 10, 2, 'Bahasa Indonesia', 80.00, 78.00, 82.00, 80.20, 1, 0, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(25, 12, 3, 'PAI', 89.00, 70.00, 75.00, 77.70, 1, 0, '2026-06-04 11:57:42', '2026-06-04 11:57:42'),
(26, 14, 1, 'IPA', 50.00, 70.00, 84.00, 69.60, 0, 0, '2026-06-04 16:47:50', '2026-06-04 16:47:50');

-- --------------------------------------------------------

--
-- Struktur dari tabel `siswa`
--

CREATE TABLE `siswa` (
  `id` int NOT NULL,
  `nis` varchar(20) NOT NULL,
  `nama` varchar(100) NOT NULL,
  `kelas` varchar(20) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data untuk tabel `siswa`
--

INSERT INTO `siswa` (`id`, `nis`, `nama`, `kelas`, `created_at`, `updated_at`, `deleted_at`) VALUES
(1, '2024001', 'Budi Santoso', 'X-IPA-1', '2026-06-04 01:14:21', '2026-06-04 01:14:21', NULL),
(2, '2024002', 'Ani Wijayanti', 'X-IPA-1', '2026-06-04 01:14:21', '2026-06-04 01:14:21', NULL),
(3, '2024003', 'Citra Dewi Lestari', 'X-IPA-1', '2026-06-04 01:14:21', '2026-06-04 01:14:21', NULL),
(4, '2024004', 'Doni Prasetyo', 'X-IPA-1', '2026-06-04 01:14:21', '2026-06-04 01:14:21', NULL),
(5, '2024005', 'Eka Fitriani', 'X-IPA-1', '2026-06-04 01:14:21', '2026-06-04 01:14:21', NULL),
(6, '2024006', 'Fajar Hidayat', 'X-IPA-2', '2026-06-04 01:14:21', '2026-06-04 01:14:21', NULL),
(7, '2024007', 'Gita Permata Sari', 'X-IPA-2', '2026-06-04 01:14:21', '2026-06-04 01:14:21', NULL),
(8, '2024008', 'Hendra Gunawan', 'X-IPA-2', '2026-06-04 01:14:21', '2026-06-04 01:14:21', NULL),
(9, '2024009', 'Intan Nurhaliza', 'X-IPA-2', '2026-06-04 01:14:21', '2026-06-04 01:14:21', NULL),
(10, '2024010', 'Joko Widodo', 'X-IPA-2', '2026-06-04 01:14:21', '2026-06-04 01:14:21', NULL),
(11, '202612379', 'Niko Dwicahyo ', '4IA08', '2026-06-04 11:31:05', '2026-06-04 11:53:14', '2026-06-04 11:53:14'),
(12, '20260292', 'Niko Dwicahyo', '4IA08', '2026-06-04 11:54:27', '2026-06-04 11:54:27', NULL),
(13, '2026029', 'Niko Dwicahyo Widiyanto', 'X-IPA-3', '2026-06-04 16:09:37', '2026-06-04 16:09:37', NULL),
(14, '20260291', 'Bambang', 'XII-IPA-3', '2026-06-04 16:38:34', '2026-06-04 16:38:34', NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(10) NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `siswa_id` int DEFAULT NULL,
  `guru_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id`, `username`, `password_hash`, `role`, `is_active`, `siswa_id`, `guru_id`, `created_at`, `updated_at`) VALUES
(1, 'admin', 'scrypt:32768:8:1$YYDn50DuBPV117ss$fa83d4555f080419c6391a7b093c987a2ae103b44fba88e2e4965416cfe95ed40c8688918192158dd47b947915f9bdb0c9a42d04a647760c77fdf959acaa0b0b', 'admin', 1, NULL, NULL, '2026-06-04 01:14:20', '2026-06-04 01:14:20'),
(2, 'GR-001', 'scrypt:32768:8:1$3rz5IDvFVmjUb1MP$9d27e49186840554f0f37ac30db268b8a2973ae079bea165ddbf8e34003c0bef7de54a158d6b5f40637d697a04c1c09f42bc174351a8548087fa7cbeddd083cf', 'guru', 1, NULL, 1, '2026-06-04 01:14:20', '2026-06-04 01:14:20'),
(3, 'GR-002', 'scrypt:32768:8:1$NqNUq6r7BboVAqQN$5aa3b525c7dccbb1db15db38e550541cbcfce2d9a1648862351d520ab5c910f65303c9f189af308564065a4e0eca4c906db5b88ff82255c76ab5754a08c01a4a', 'guru', 1, NULL, 2, '2026-06-04 01:14:20', '2026-06-04 01:14:20'),
(4, 'GR-003', 'scrypt:32768:8:1$30hQMZmFV7OFCHbX$b4eb822a7aab7fc7a6b9abfed61437ec1c136e9803275b195d299fcd2704448d971b4f18e4726a5b0905588d9c2c791191d7f69d22ab6a4e25afc067d5f5c552', 'guru', 1, NULL, 3, '2026-06-04 01:14:21', '2026-06-04 01:14:21'),
(5, '2024001', 'scrypt:32768:8:1$OXhaaO02BjXhmnFW$78c3c2dffab79b9381a5de3d87de2b3dfd6c3358d55121f9d40400ebe10348d1a3689b21ae5b4cd871f0d45b7cc6735bf1c837b4f46a59362d7ebeaa2c96ed76', 'siswa', 1, 1, NULL, '2026-06-04 01:14:21', '2026-06-04 01:14:21'),
(6, '2024002', 'scrypt:32768:8:1$S4b8Ugu7kCevzhl4$dc294bbb833f4dc668bdcb703baa3bc79d6a5a12ff3e597d1efee80a722d924b3c90569e5bbcca79a189c7ef54f84d6a46e6f4a159ee59ec6dc7ca21e2191183', 'siswa', 1, 2, NULL, '2026-06-04 01:14:21', '2026-06-04 01:14:21'),
(7, '2024003', 'scrypt:32768:8:1$UhJohl5aXwYwgDZa$558f79eba88774d102c4b49a6d9b0fba3501dd2b708c3f8108d2156982caf19d85b20b0f4897aa0a9cc044daaa4acb98466d0da44ea53a06cac6e481abb066fa', 'siswa', 1, 3, NULL, '2026-06-04 01:14:21', '2026-06-04 01:14:21'),
(8, '2024004', 'scrypt:32768:8:1$S5PZgcl6kciUTMT2$6689010b77f9fb017b3ab450769c7e6db68e09227cdfd4ee0e03fea6c1a82a492c4a50a4809caf41568eb35edc0c1870010f0ae969eb233adfb63ebe93605b4a', 'siswa', 1, 4, NULL, '2026-06-04 01:14:21', '2026-06-04 01:14:21'),
(9, '2024005', 'scrypt:32768:8:1$TdByipqh0a0VV1s9$e81d56a3ff3ea06389de55dee409b278f05e9b88093a05e233545cbf16ddaa756f5f63380beed6000c2af726c147cbd11c6c0955a59230f9abde431ea5f5c3d9', 'siswa', 1, 5, NULL, '2026-06-04 01:14:21', '2026-06-04 01:14:21'),
(10, '2024006', 'scrypt:32768:8:1$zmWbTjQyEPYuntmn$e032c48da2130f98af9dce384731dcae27d557b81ef37f627b44e23312c0fb4a4172fe9aee094804a52bd364f6694a99dcf428d9cbe40fb493fde3d84ac038f5', 'siswa', 1, 6, NULL, '2026-06-04 01:14:21', '2026-06-04 01:14:21'),
(11, '2024007', 'scrypt:32768:8:1$kRQau2Dpr9HdnuFj$1933992be5a271ec93589b43cee595e3dd40e3d1d1109faa90876183eb2cfffdc403ec05b9afeb68d889e78e7d27cebc6c280b5a2ce72718b1c52089faf3d0d7', 'siswa', 1, 7, NULL, '2026-06-04 01:14:21', '2026-06-04 01:14:21'),
(12, '2024008', 'scrypt:32768:8:1$Y4SuEvqsGcqbT3Gb$b4cb4ede9caa57972b5b61cc257d2375ccb4a9c266b902effafc1d8095303f2f15138475337520bb58d6d8e75cb005c6476b0cb9cce5ac6e7954f70831ceb18e', 'siswa', 1, 8, NULL, '2026-06-04 01:14:21', '2026-06-04 01:14:21'),
(13, '2024009', 'scrypt:32768:8:1$mNlGg0zYym144ZYe$a8f96b81cda0b247c39f7de8cbae438f644921a1894ffd7dec6428287c3da6aa81ac88f3dee9b30b873f63478c7d23ae746b5e49f4c4c1840629834c5da636d8', 'siswa', 1, 9, NULL, '2026-06-04 01:14:21', '2026-06-04 01:14:21'),
(14, '2024010', 'scrypt:32768:8:1$mrLwESUbtPLl2pj1$9758ddcde904d6a93513e9a95d1352275e026d842721a1e277536106c345a1348fab2f01c6ad7b43dcd7989ea23f2ec9fff1ed21b30a402dbcf76f46c3aab247', 'siswa', 1, 10, NULL, '2026-06-04 01:14:22', '2026-06-04 01:14:22'),
(15, 'GR-004', 'scrypt:32768:8:1$88mj4wdameNv40AG$cfdf279e74e49468253fbd24e956a010ac096201f38c23d6dbc37cbcd7e55ae7a147e7c15259a9b411d00b45a545fdc0493d473f1d1097879eaf551be597b7cb', 'guru', 1, NULL, 4, '2026-06-04 08:38:19', '2026-06-04 16:41:22'),
(17, 'GR-005', 'scrypt:32768:8:1$VC2SlUVxItY2ffcv$3e0fa07d3f36ddacb59dd1c5cf238a31c4fee3397eb7ff7ee9d02c8095a21b56e4427915dfe981eb284492bd534ce7bc1864062e78771784a240aabe075d1e1d', 'guru', 1, NULL, 5, '2026-06-04 11:53:46', '2026-06-04 16:41:54'),
(18, '20260292', 'scrypt:32768:8:1$AQYoPwnbw1JTMmr3$d50969ee82595bc654fde9885654a88ad2c0654dca0e7d5deb808b768bd84bee2e09d4cecb46264fc469f8d523371a026e9727d8eb2c8d32519d23684157d24d', 'siswa', 1, 12, NULL, '2026-06-04 11:54:27', '2026-06-04 11:54:27'),
(19, '2026029', 'scrypt:32768:8:1$MQHOQ9f8bdp6CHXT$350c6946986e21e232c848e6adceb7201e508dae0786bd45b13950bb964917f9041f5a9b5b99070a6e7ce4839559f700cb51a5e30833893aed21510dfd889530', 'siswa', 1, 13, NULL, '2026-06-04 16:09:37', '2026-06-04 16:09:37'),
(20, 'GR-006', 'scrypt:32768:8:1$IXcXwmfeselZg4of$d5b136febc685a3c249c428fae3abe1b17b68e34546e1e96abd17030b5494980f0f7e97e73397d2dec9581bcf061b9c46a2a9ea6d767219fc0ff30c5cb953539', 'guru', 1, NULL, 11, '2026-06-04 16:12:10', '2026-06-04 16:42:15'),
(21, '20260291', 'scrypt:32768:8:1$YHnl9Z8zTUCPFsHP$b20ba4954325afd72a3cf154f9a2c1d1cee4261d4d4cf9da00f2b00dc096c9fd801925fe642b98e44e9ea32b7c43a1dfa549fd648bb2ca989a94db700fe97048', 'siswa', 1, 14, NULL, '2026-06-04 16:38:34', '2026-06-04 16:38:34'),
(22, 'GR-007', 'scrypt:32768:8:1$dDz36xltRSpMizaG$1ed009a85b55b9bd7bb6efe8890292f8fb790d313700208b9d731ec5395ba85265974f9a6ea41cdf9e4adfe2da7f594a4f697cd39d0e527f90eea53edab78c07', 'guru', 1, NULL, 12, '2026-06-04 16:40:13', '2026-06-04 16:40:13');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indeks untuk tabel `audit_log`
--
ALTER TABLE `audit_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indeks untuk tabel `guru`
--
ALTER TABLE `guru`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id_guru` (`id_guru`);

--
-- Indeks untuk tabel `nilai`
--
ALTER TABLE `nilai`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_siswa_mapel` (`siswa_id`,`mata_pelajaran`),
  ADD KEY `guru_id` (`guru_id`);

--
-- Indeks untuk tabel `siswa`
--
ALTER TABLE `siswa`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_siswa_nis` (`nis`),
  ADD KEY `ix_siswa_kelas` (`kelas`);

--
-- Indeks untuk tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_users_username` (`username`),
  ADD KEY `guru_id` (`guru_id`),
  ADD KEY `siswa_id` (`siswa_id`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `audit_log`
--
ALTER TABLE `audit_log`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- AUTO_INCREMENT untuk tabel `guru`
--
ALTER TABLE `guru`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT untuk tabel `nilai`
--
ALTER TABLE `nilai`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `siswa`
--
ALTER TABLE `siswa`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `audit_log`
--
ALTER TABLE `audit_log`
  ADD CONSTRAINT `audit_log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Ketidakleluasaan untuk tabel `nilai`
--
ALTER TABLE `nilai`
  ADD CONSTRAINT `nilai_ibfk_1` FOREIGN KEY (`guru_id`) REFERENCES `guru` (`id`),
  ADD CONSTRAINT `nilai_ibfk_2` FOREIGN KEY (`siswa_id`) REFERENCES `siswa` (`id`);

--
-- Ketidakleluasaan untuk tabel `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`guru_id`) REFERENCES `guru` (`id`),
  ADD CONSTRAINT `users_ibfk_2` FOREIGN KEY (`siswa_id`) REFERENCES `siswa` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
